from __future__ import annotations

from types import ModuleType
from typing import Any

from .base import Empty, SymbolDescriptor, SymbolDictionnary

__all__ = ["SymbolReference", "SymbolTable"]


def _get_full_class_name(cls):
    """Get the full qualified class name including module."""
    return f"{cls.__module__}.{cls.__qualname__}"


class SymbolReference(SymbolDescriptor):
    """Represents an import reference with optional alias."""
    
    __slots__ = SymbolDescriptor.__slots__ + ("_alias",)

    def __init__(self, name: str, *, alias: str | None = None, annotation: Any | None = Empty):
        super().__init__(name=name, kind="import", annotation=annotation)
        self._alias: str | None = alias

    @property
    def alias(self) -> str | None:
        return self._alias

    @property
    def aliased_name(self) -> str:
        return self._alias if self._alias else self.name

    def __str__(self) -> str:
        if self._alias:
            return f"import {self.qualified_name} as {self._alias}"
        else:
            return f"import {self.qualified_name}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SymbolReference):
            return NotImplemented
        return (
            self.name == other.name
            and self.alias == other.alias
            and self.kind == other.kind
            and self.annotation == other.annotation
            and self.scope == other.scope
        )


class SymbolTable(SymbolDictionnary[SymbolReference]):
    """Symbol table to import in module with import directive."""

    def add(self, symbol: SymbolReference, ignore_duplicate: bool = True) -> SymbolReference:
        if symbol.kind != "import":
            raise ValueError(f"Expected an import, got a {symbol.kind}")
        return super().add(symbol, ignore_duplicate=ignore_duplicate)

    def add_reference(self, name: str, *, alias: str | None = None, annotation: Any | None = Empty) -> SymbolReference:
        """Add a symbol reference with optional alias."""
        return self.add(SymbolReference(name=name, alias=alias, annotation=annotation))

    def add_module(self, name: str, alias: str | None = None) -> SymbolReference:
        """Add a module reference."""
        module_name = name if name.endswith(".*") else f"{name}.*"
        return self.add(symbol=SymbolReference(name=module_name, annotation=ModuleType))

    def add_class(self, cls: type[Any]) -> SymbolReference:
        """Add a class reference."""
        module = cls.__module__
        if module.startswith("builtins"):
            raise RuntimeWarning("You shouldnt reference builtins module")
        return self.add(symbol=SymbolReference(name=_get_full_class_name(cls), annotation=cls))

    def add_function(self, func: Any) -> SymbolReference:
        """Add a function reference."""
        module = func.__module__
        if module.startswith("builtins"):
            raise RuntimeWarning("You shouldnt reference builtins module")
        return self.add(SymbolReference(name=func.__qualname__, annotation=type(func)))