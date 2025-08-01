
import warnings
from asyncio import AbstractEventLoop, get_event_loop, new_event_loop, run_coroutine_threadsafe, set_event_loop
from collections.abc import Callable, Coroutine
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
from inspect import getattr_static, getmembers, getmro, isawaitable, iscoroutinefunction
from threading import Event as ThreadEvent
from threading import Thread
from typing import Any, TypeVar, cast
from weakref import WeakKeyDictionary, WeakValueDictionary

from curio import UniversalEvent

__all__ = ["init_asyncio_loop", "run_in_asyncio", "AsyncioKernel", "asyncio_context"]

T = TypeVar("T", bound=type[Any])
Y = TypeVar("Y")

def init_asyncio_loop(max_workers: int = 2, termination_timeout:int = 30) -> Callable[[], None]:
    """Boostrap asyncio loop on a dedicated thread.
    
    Args:
        max_workers (int): The maximum number of threads that can be used to execute asyncio coroutine, default 2.
        termination_timeout (int): Termination timeout of daemon, default 30 seconds.

    Returns: 
        (Callable[[], None]): termination handler

    """

    def _run_loop_forever( start_event: ThreadEvent, loop: AbstractEventLoop) -> Callable[[], None]:
        """Returns run_loop_forever method."""
        def run_loop_forever():
             # set loop in deamon thread
            set_event_loop(loop)
            # signal start
            start_event.set()
            # run asyncio loop forever
            loop.run_forever()

        return run_loop_forever

    def _terminate(loop, daemon_thread, termination_timeout) -> Callable[[], None]:
        """Returns terminate handler."""
        def terminate():
            # Schedule shutdown tasks before stopping the loop
            async def shutdown_sequence():
                await loop.shutdown_asyncgens()
                await loop.shutdown_default_executor()
                loop.stop()
            
            try:
                future = run_coroutine_threadsafe(shutdown_sequence(), loop)
                future.result(timeout=termination_timeout)
            except Exception:
                loop.call_soon_threadsafe(loop.stop) # pause/exit the loop while it’s running
            daemon_thread.join(timeout=termination_timeout)
            
            # Close the loop after daemon thread has finished
            if not loop.is_closed():
                loop.close()

        return terminate

    # create asyncio loop
    _asyncio_loop = new_event_loop()
    _asyncio_loop.set_default_executor(ThreadPoolExecutor(max_workers=max_workers))
    
    # define asyncio loop in curio/main thread
    set_event_loop(_asyncio_loop)

    # Boot the asyncio worker thread
    start_event = ThreadEvent()
    _daemon_thread = Thread(target=_run_loop_forever(start_event=start_event, loop=_asyncio_loop), name="asyncio-daemon")
    _daemon_thread.start()
    # wait for daemon start
    start_event.wait()

    # return terminate function
    return _terminate(loop=_asyncio_loop, daemon_thread=_daemon_thread, termination_timeout=termination_timeout)


def run_in_asyncio(func: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
    """Decorator to run an asyncio coroutine from a Curio coroutine context.

    It schedules the coroutine on the asyncio loop running in a separate thread,
    waits for the result using a Curio-friendly UniversalEvent, and returns the result
    without blocking the Curio kernel.

    Notes:
        - wrapped function contains attributs `_asyncio_wrapped` equal to True
    """
    
    @wraps(func)
    async def wrapper(*args, **kwargs):

         # Get the currently running asyncio loop
        loop = get_event_loop()
        if not loop:
            raise RuntimeError("No running asyncio event loop found")
    
         # UniversalEvent allows Curio to wait for a result safely across threads
        event = UniversalEvent()

        # Placeholders to store result or error from asyncio coroutine
        result : Any|None = None
        error : Exception  | None = None

        async def _runner():
            """Coroutine to actually run the target asyncio callable."""
            nonlocal result, error
            try:
                result = await func(*args, **kwargs)
            except Exception as e:
                error = e
            finally:
                await event.set()  # Notify the Curio side that result is ready

        # Schedule the coroutine to run in the asyncio thread's loop
        run_coroutine_threadsafe(_runner(), loop)
        
        # Wait on the event in Curio
        await event.wait()

        if error:
            raise error # type: ignore [reachability]
        return result

    wrapper._asyncio_wrapped = True # type: ignore
    return wrapper



def class_proxy_wrapper(base_cls: type[Y]) -> type[Y]:
    class Proxy(base_cls):
        __name__ = f"{base_cls.__name__}Proxy"
        __slots__ = ('_target',)

        def __init__(self, *args, **kwargs):
            self._target = base_cls(*args, **kwargs)


        def __getattr__(self, name: str) -> Any:
            attr = getattr(self._target, name)

            if iscoroutinefunction(attr) and not getattr(attr, "_asyncio_wrapped", False):
                # Optional: wrap async methods (external calls)
                return run_in_asyncio(attr)
            return attr

        def __setattr__(self, name: str, value: Any) -> None:
            if name == "_target":
                super().__setattr__(name, value)
            else:
                setattr(self._target, name, value)

        def __repr__(self):
            return f"<Proxy for {repr(self._target)}>"
        
        # Dynamically override coroutine methods
        def __init_subclass__(cls, **kwargs):
            super().__init_subclass__(**kwargs)

            for name, method in getmembers(cls, predicate=iscoroutinefunction):
                if name.startswith("__"):
                    continue
                if getattr(method, "_asyncio_wrapped", False):
                    continue
                wrapped = run_in_asyncio(method)
                setattr(cls, name, wrapped)


    return Proxy # type: ignore

class AsyncProxyWrapperMixin:
    """
    Mixin that wraps async methods on external access via __getattribute__,
    including support for inherited and property-like access,

    Notes:
        - Optimized using class-level caching and `__init_subclass__`
        - Inner call of a proxied class will call the original method
    """
    _method_cache: WeakKeyDictionary[object, Callable] = WeakKeyDictionary()
    _descriptor_keys: dict[str, object] = {}

    def __getattribute__(self, name: str) -> Any:
        attr = super().__getattribute__(name)

        if name.startswith("__"):
            return attr

        # Fast-path for coroutine methods
        cache = self._method_cache
        key = self._descriptor_keys.get(name)

        # Direct coroutine function
        if iscoroutinefunction(attr):
            if key and key in cache:
                return cache[key].__get__(self, type(self))
            wrapped = run_in_asyncio(attr)
            if key:
                cache[key] = wrapped
            return wrapped.__get__(self, type(self))

        # Coroutine-returning descriptors (like async properties)
        if isawaitable(attr):
            if key and key in cache:
                return cache[key]()  # call cached coroutine wrapper

            async def descriptor_wrapper():
                return await attr
            
            wrapped = run_in_asyncio(descriptor_wrapper)
            if key:
                cache[key] = wrapped
            return wrapped()   # return coroutine object (not awaited)

        return attr



    def __init_subclass__(cls) -> None:
        """Preload descriptor keys and wrap async methods."""
        super().__init_subclass__()

        cls._descriptor_keys = {}
        cls._method_cache = WeakKeyDictionary()

        for base in getmro(cls):
            if base is object:
                continue
            for name, attr in vars(base).items():
                if name.startswith("__"):
                    continue
                try:
                    descriptor = getattr_static(cls, name)
                except AttributeError:
                    descriptor = name  # fallback key
                    # inspect.getattr_static fails for things like @property, 
                    # __getattr__-delegated attributes, or dynamically added members. 
                    # Using name ensures the method can still be wrapped and looked up
                    # even if it’s not statically findable noqa: E501

                cls._descriptor_keys[name] = descriptor

                if iscoroutinefunction(attr) and not getattr(attr, "_asyncio_wrapped", False):
                    cls._method_cache[descriptor] = run_in_asyncio(attr)




def has_dynamic_attrs_in_mro(cls: type) -> list[str]:
    """
    Check if any class in the MRO allows dynamic attributes or weakrefs.
    Returns a list of incompatible base class names.
    """
    incompatible = []
    for base in getmro(cls):
        if base is object:
            continue

        base_slots = getattr(base, "__slots__", None)

        if base_slots is None:
            incompatible.append(base.__name__)
        else:
            if isinstance(base_slots, str):
                base_slots = [base_slots]
            if "__dict__" in base_slots or "__weakref__" in base_slots:
                incompatible.append(base.__name__)
    return incompatible

class AsyncProxyMeta(type):
    """
    Wrap coroutine methods and async properties once per class hierarchy,
    cache wrapped results, and store originals as _original_<name>.
    """

    def __new__(mcs, name, bases, namespace):

        # Check for slot compatibility
        dummy_cls = type(name, bases, {})
        dynamic_bases = has_dynamic_attrs_in_mro(dummy_cls)
        if dynamic_bases:
            warnings.warn(
                f"[AsyncProxyMeta] Cannot safely apply '__slots__ = ()' to {name} due to dynamic attributes "
                f"allowed in: {', '.join(dynamic_bases)}. Skipping slots.",
                RuntimeWarning,
                stacklevel=2
            )
        else:
            namespace.setdefault("__slots__", ())

        cls = super().__new__(mcs, name, bases, namespace)

         # Initialize or reuse cache dict on class
        if not hasattr(cls, "_async_wrap_cache"):
            cls._async_wrap_cache = {} # type: ignore


        for base in getmro(cls):
            if base is object:
                continue
            for attr_name, attr in vars(base).items():
                if attr_name.startswith("__"):
                    continue
                
                if attr_name in cls._async_wrap_cache: # type: ignore
                    # Already wrapped and cached
                    continue

                # Wrap coroutine methods
                if iscoroutinefunction(attr):
                    original = getattr(cls, attr_name, attr)
                    wrapped = run_in_asyncio(attr)
                    setattr(cls, attr_name, wrapped)
                    setattr(cls, f"_original_{attr_name}", original)
                    cls._async_wrap_cache[attr_name] = wrapped # type: ignore

                # Wrap coroutine-style properties
                elif isinstance(attr, property):
                    fget = attr.fget
                    if fget and iscoroutinefunction(fget):
                        wrapped_fget = run_in_asyncio(fget)
                        wrapped_prop = property(wrapped_fget, attr.fset, attr.fdel)
                        setattr(cls, attr_name, wrapped_prop)
                        setattr(cls, f"_original_{attr_name}", attr)
                        cls._async_wrap_cache[attr_name] = wrapped_prop # type: ignore

        return cls




class AsyncProxyMetaMixin:
    """
    Mixin that wraps async methods on external access via __getattribute__,
    including support for inherited and property-like access,

    Intercept attribute access:
      - External calls → wrapped coroutine methods/properties
      - Internal calls (self.method()) → original unwrapped coroutine methods/properties
  
    Notes:
        - Optimized using class-level caching and `__init_subclass__`
        - Inner call of a proxied class will call the original method
    """
    _method_cache: WeakKeyDictionary[object, Callable] = WeakKeyDictionary()
    _descriptor_keys: dict[str, object] = {}

    def __getattribute__(self, name: str) -> Any:
        attr = super().__getattribute__(name)

        # Ignore dunder methods and attributes that don't start with _original_
        if name.startswith("__") or name.startswith("_original_"):
            return attr

        # If method is wrapped, return original on internal calls
        # We detect internal calls by the presence of frame.f_back.f_locals['self'] == self
       
        import sys

        try:
            frame = sys._getframe(1)  # caller frame
            caller_self = frame.f_locals.get("self", None)
        except Exception:
            caller_self = None

        if caller_self is self:
            # Internal call: return original method if available
            original_name = f"_original_{name}"
            if hasattr(self, original_name):
                return getattr(self, original_name)

        return attr
    



_proxy_cache: WeakValueDictionary[type, type] = WeakValueDictionary()

def class_wrapper(base_cls: T) -> T:
    """
    Wraps a class with the AsyncProxyMeta metaclass and caches the subclass.
    """
    if base_cls in _proxy_cache:
        return cast(T, _proxy_cache[base_cls])
    
    
    class Proxy(base_cls, AsyncProxyMetaMixin,  metaclass=AsyncProxyMeta):
        __name__ = f"{base_cls.__name__}Wrapped"
        __qualname__ = f"{base_cls.__qualname__}Wrapped"
    
    _proxy_cache[base_cls] = Proxy
    return Proxy


def asyncio_context(base_cls: T) -> T:
    """Runs all async methods of a class in asyncio lopp.
    `asyncio_context` is a class decorator, and apply `run_in_asyncio` to all async methods in a class, 
    including support for inherited and property-like access, 
    without affecting internal self.method() calls.

    Usage:
        @asyncio_context
        class MyAsyncClass:
            async def foo(self, x):
                return x * 2

            async def bar(self, y):
                return y + 1

    MyAsyncClass can be used from curio async context.
    """
    dynamic_bases = has_dynamic_attrs_in_mro(base_cls)
    class Proxy(base_cls, AsyncProxyWrapperMixin):
        __name__ = f"{base_cls.__name__}Wrapped"
        __qualname__ = f"{base_cls.__qualname__}Wrapped"
        if not dynamic_bases:
            __slots__ = ()  # Avoid adding per-instance dicts if not needed
        
    return Proxy



class AsyncioKernel:
    """A context manager for asyncio."""
    _terminate_handler: Callable[[], None]
    
    def __init__(self, max_workers: int = 2, termination_timeout:int = 30):
        self._terminate_handler = init_asyncio_loop(max_workers=max_workers, termination_timeout=termination_timeout)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._terminate_handler()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._terminate_handler()
    

    async def run(self, func: Callable[..., Coroutine], *args, **kwargs):
        """Run an asyncio coroutine from a Curio coroutine context."""
        return await run_in_asyncio(func)(*args, **kwargs)

