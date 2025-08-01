#from curio.meta import iscoroutinefunction
from collections.abc import Awaitable, Callable
from functools import partial, wraps
from inspect import isasyncgenfunction as _isasyncgenfunction
from inspect import isawaitable as _isawaitable
from inspect import iscoroutinefunction as _iscoroutinefunction
from types import CoroutineType
from typing import Any, TypeVar

T = TypeVar('T', bound=Callable[..., Any])

__all__ = ["ensure_async", "iscoroutinefunction", "ensure_awaitable"]



def ensure_async(target: T) -> T | Callable[..., Awaitable[Any]]:
    """Wrap a sync function into an async one if needed.
    
    Args:
        target: Function or callable to ensure is async
        
    Returns:
        Async function or the original if already async
        
    Raises:
        TypeError: If target is a coroutine object
        
    Note:
        Only handles functions/callables. Use ensure_awaitable for coroutine objects.
    """
    if isinstance(target, CoroutineType):
        raise TypeError("Cannot wrap coroutine object - use ensure_awaitable instead") 
    
    if iscoroutinefunction(target):
        return target
    
    @wraps(target)
    async def wrapped(*args, **kwds):
        return target(*args, **kwds)
    
    return wrapped

def ensure_awaitable(target: Callable | CoroutineType | Any) -> Awaitable[Any]:
    """Ensure target is awaitable, handling both functions and coroutine objects.
    
    Args:
        target: Function, coroutine object, or awaitable to ensure is awaitable
        
    Returns:
        Awaitable object
        
    Note:
        Coroutine objects are returned as-is (single use)
        Functions are wrapped if needed
    """
    if isinstance(target, CoroutineType):
        return target
    
    if _isawaitable(target):
        return target
    
    if iscoroutinefunction(target):
        return target()
    
    async def wrapped():
        return target() if callable(target) else target
    
    return wrapped()

def iscoroutinefunction(func) -> bool:
    """Check if a function or object is a coroutine function or coroutine-like.
    
    Detects:
    - Standard coroutine functions (async def)
    - Partial functions wrapping coroutines
    - Bound methods of coroutines
    - Direct coroutine objects
    - Callable objects with async __call__
    - Awaitable objects
    - Objects with __await__ method
    - Objects with _awaitable attribute
    - Async generators
    
    Args:
        func: Function, method, or object to check
        
    Returns:
        bool: True if func is coroutine-like, False otherwise
    """
    if isinstance(func, partial):
        return _iscoroutinefunction(func.func)
    if hasattr(func, '__func__'):
        return _iscoroutinefunction(func.__func__)
    if isinstance(func, CoroutineType):
        return True
    if callable(func) and _iscoroutinefunction(func.__call__):
        return True
    return (_iscoroutinefunction(func) or _isawaitable(func) or 
            hasattr(func, "__await__") or hasattr(func, '_awaitable') or 
            _isasyncgenfunction(func))


