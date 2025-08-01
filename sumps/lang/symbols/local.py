from __future__ import annotations

import uuid
from inspect import isbuiltin, isclass, isfunction, ismethod, ismodule
from typing import Any
from weakref import ref

from .base import Empty, SymbolDescriptor, SymbolDictionnary, SymbolKind

__all__ = ["LocalSymbol", "LocalSymbolTable"]


def _classify_object(obj) -> SymbolKind:
    """Determines the kind of a Python object using introspection."""
    if ismodule(obj):
        return "module"
    elif isclass(obj):
        return "class"
    elif isfunction(obj) or ismethod(obj) or isbuiltin(obj):
        return "function"
    return "variable"


def _is_lambda(func):
    """Check if a function is a lambda function."""
    return callable(func) and func.__name__ == "<lambda>"


def _get_function_name(func):
    """Get the name of a function or callable object."""
    if hasattr(func, '__name__'):
        return func.__name__
    elif hasattr(func, '__class__'):
        return func.__class__.__name__
    return str(func)


class LocalSymbol(SymbolDescriptor):
    """Represents a runtime-local symbol, with an actual object reference (possibly weak)."""

    _reference: Any
    __slots__ = SymbolDescriptor.__slots__ + ("_ref", "_weak")

    def __init__(self, name: str, reference: Any, annotation: Any | None = Empty) -> None:
        if reference is None:
            raise ValueError("LocalSymbol must have a reference.")

        if annotation is Empty:
            annotation = type(reference)

        super().__init__(name=name, kind=_classify_object(reference), annotation=annotation)

        try:
            self._ref = ref(reference)
            self._weak = True
        except TypeError:
            self._ref = reference
            self._weak = False

    @property
    def reference(self) -> Any:
        """Returns the actual object, or raises if it was weakly referenced and collected."""
        if self._weak:
            obj = self._ref()
            if obj is None:
                raise ReferenceError("The referenced object has been garbage collected.")
            return obj
        return self._ref

    @property
    def is_weak_reference(self) -> bool:
        return self._weak

    def __repr__(self) -> str:
        def truncate(value: str, max_len: int = 80) -> str:
            if len(value) > max_len:
                return value[: max_len - 3] + "..."
            return value

        if self._weak:
            obj = self._ref()
            ref_repr = "<collected>" if obj is None else truncate(repr(obj))
        else:
            ref_repr = truncate(repr(self._ref))

        return (
            f"{self.__class__.__name__}("
            f"name={self.name!r}, kind={self.kind!r}, annotation={self.annotation!r}, "
            f"scope={self.scope!r}, weak_ref={self._weak}, reference={ref_repr})"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return (
            self.name == other.name
            and self.kind == other.kind
            and self.annotation == other.annotation
            and self.scope == other.scope
            and self.reference == other.reference
        )
    
    def __hash__(self) -> int:
        return hash((self.name, self.kind, str(self.annotation), self.scope, id(self.reference)))


class LocalSymbolTable(SymbolDictionnary[LocalSymbol]):
    """Symbol table for runtime-local symbols with object references."""

    def add(self, symbol: LocalSymbol, ignore_duplicate: bool = True):
        """Add a local symbol to the table."""
        if symbol.kind not in ("variable", "function", "class"):
            raise ValueError(f"Expected a variable or function or class, got a {symbol.kind}")
        return super().add(symbol, ignore_duplicate=ignore_duplicate)

    def add_class(self, cls: type[Any], ignore_duplicate: bool = True) -> LocalSymbol:
        """Add a class to the symbol table."""
        module = cls.__module__
        if module.startswith("builtins"):
            raise RuntimeWarning("You shouldnt reference builtins module")
        return self.add(symbol=LocalSymbol(name=cls.__qualname__, reference=cls), ignore_duplicate=ignore_duplicate)

    def add_function(self, func: Any, ignore_duplicate: bool = True, support_lambda: bool = True) -> LocalSymbol:
        """Add a function to the symbol table."""
        if not callable(func):
            raise ValueError(f"Expected a callable, got a {type(func)}")
        
        module = func.__module__
        if module == "builtins":
            raise RuntimeWarning("You shouldnt reference builtins module")
        
        if _is_lambda(func):
            if not support_lambda:
                raise RuntimeWarning("You shouldnt reference lambda functions")
            func.__name__ = f"lambda_{uuid.uuid4().hex}"
        
        return self.add(symbol=LocalSymbol(name=_get_function_name(func), reference=func), ignore_duplicate=ignore_duplicate)

    def add_variable(self, name: str, value: Any) -> LocalSymbol:
        """Add a variable to the symbol table."""
        module = value.__module__
        if module == "builtins":
            raise RuntimeWarning("You shouldnt reference builtins module")
        return self.add(LocalSymbol(name=name, reference=value))