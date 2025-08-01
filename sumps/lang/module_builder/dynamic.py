from __future__ import annotations

import sys
import weakref
from functools import wraps
from importlib import invalidate_caches
from types import MethodType, ModuleType
from typing import Any, TypeVar

__all__ = ["DynamicModule", "DynamicModuleManager"]

_T = TypeVar("_T")
_FUNC = TypeVar("_FUNC", bound=callable)


class DynamicModule:
    """A dynamic module wrapper with unload capabilities.

    Provides safe access to dynamically created modules with the ability to cleanly
    unload them from memory. The unload() method removes the module from sys.modules,
    clears its dictionary, and breaks strong references to enable garbage collection.
    """

    __slots__ = ("__name__", "_module", "_weakref")

    def __init__(self, module: ModuleType, store_in_sys_modules: bool = False):
        """Initialize DynamicModule wrapper.

        Args:
            module: The ModuleType instance to wrap.
            store_in_sys_modules: If True, registers module in sys.modules for import access.
        """
        self.__name__: str = module.__name__
        self._module: ModuleType | None = module
        self._weakref: weakref.ReferenceType[ModuleType] = weakref.ref(self._module)

        # Optional: store in sys.modules (optional depending on integration)
        if store_in_sys_modules:
            sys.modules[self.__name__] = self._module

    @property
    def module(self) -> ModuleType | None:
        return self._weakref()

    @property
    def name(self):
        return self.__name__

    def unload(self):
        if self.__name__ in sys.modules:
            del sys.modules[self.__name__]
        if self._module:
            self._module.__dict__.clear()
        self._module = None  # break strong reference
        invalidate_caches()

    def is_unloaded(self):
        """Returns True if the module has been unloaded and garbage collected."""
        return self._weakref() is None

    def __repr__(self):
        return f"<DynamicModule {self.__name__}>"

    def get_reference[_T](self, name: str, annotation: type[_T] | None = None) -> _T:
        """Get a reference to a symbol from the module.

        Args:
            name: Symbol name to retrieve.
            annotation: Optional type annotation for validation.
        """
        if not self._module:
            raise ReferenceError("The referenced module no longer exists.")

        if hasattr(self._module, name):
            ref = getattr(self._module, name)
            if annotation and not isinstance(ref, annotation):
                raise TypeError(f"Symbol '{name}' is not of type {annotation}")
            return ref

        raise AttributeError(f"Symbol '{name}' not found in module '{self.__name__} {dir(self._module)}'")

    def get_weak_reference[_T](self, attr: str, annotation: type[_T] | None = None) -> weakref.ReferenceType[_T] | None:
        """Returns a weak reference to a module attribute, or None if not found or not referenceable.

        Args:
            attr: Attribute name to retrieve.
            annotation: Optional type annotation for validation.
        """
        module = self._weakref()
        if not module:
            return None

        value = module.__dict__.get(attr, None)
        if value is None:
            return None

        if annotation and not isinstance(value, annotation):
            raise TypeError(f"Symbol '{attr}' is not of type {annotation}")
        try:
            return weakref.ref(value)
        except TypeError:
            return None

    def get_reference_function[_FUNC](
        self, name: str, weak: bool = True, decorate: bool = True, annotation: type[_FUNC] | None = None
    ) -> _FUNC:
        """Get a function reference from the module.

        Args:
            name: Function name to retrieve.
            weak: If True, uses weak references (default).
            decorate: If True, wraps with safety decorator (default).
            annotation: Optional type annotation for validation.
        """
        fn = self.get_reference(name, annotation=annotation)
        if not callable(fn):
            raise TypeError(f"Symbol '{name}' is not callable")

        if not weak or not decorate:
            return fn

        ref = weakref.WeakMethod(fn) if isinstance(fn, MethodType) else weakref.ref(fn)

        @wraps(fn)
        def wrapper(*args, **kwargs):
            target = ref()
            if target is None:
                raise ReferenceError("The referenced function no longer exists.")
            return target(*args, **kwargs)

        return wrapper  # type: ignore


class DynamicModuleManager:
    """Singleton manager for dynamic modules with registration and lifecycle management."""

    __slots__ = ("_modules",)

    def __init__(self):
        self._modules: dict[str, DynamicModule] = {}

    def get_reference(self, name: str) -> Any:
        """Get a reference to a symbol from a registered module."""
        for module in self._modules.values():
            if hasattr(module, name):
                return getattr(module, name)

        raise AttributeError(f"Symbol '{name}' not found in any registered module")

    def register(self, module: DynamicModule):
        """Register a dynamic module for management."""
        self._modules[module.__name__] = module

    def get(self, name: str) -> ModuleType | None:
        """Get a registered module by name."""
        mod = self._modules.get(name, None)
        return mod.module if mod else None

    def unload(self, module_name: str):
        """Unload a specific module by name."""
        if module_name in self._modules:
            self._modules[module_name].unload()
            del self._modules[module_name]

    def clear(self):
        """Unload all registered modules."""
        for module in self._modules.values():
            module.unload()
        self._modules.clear()