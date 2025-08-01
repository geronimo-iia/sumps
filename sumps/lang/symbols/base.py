from __future__ import annotations

from abc import ABC
from collections import OrderedDict
from collections.abc import Iterator
from typing import Any, Generic, Literal, TypeVar

from ..stringcase import snake_case

__all__ = [
    "SymbolKind",
    "ParameterKind", 
    "Empty",
    "SymbolDescriptor",
    "SymbolVisitor",
    "SymbolDictionnary",
]

SymbolKind = Literal["variable", "function", "class", "parameter", "module", "import"]
ParameterKind = Literal["POSITIONAL_ONLY", "POSITIONAL_OR_KEYWORD", "VAR_POSITIONAL", "KEYWORD_ONLY", "VAR_KEYWORD"]

Symbol = TypeVar("Symbol", bound="SymbolDescriptor")


class Empty:
    """Marker object to indicate an intentionally 'empty' value that is not None."""
    __slots__ = ()

    def __repr__(self):
        return "<Empty>"

    def __bool__(self):
        return False


class SymbolDescriptor(ABC):
    """Abstract base class representing a generic symbol with metadata."""
    
    _name: str
    _scope: str | None
    _annotation: Any | None
    _kind: SymbolKind

    __slots__ = ("_name", "_scope", "_annotation", "_kind")

    def __init__(self, name: str, kind: SymbolKind, annotation: Any | None = Empty) -> None:
        self._scope, self._name = self._normalize_scope_and_name(full_name=name)
        self._annotation = annotation
        self._kind = kind

    @staticmethod
    def _normalize_scope_and_name(full_name: str) -> tuple[str | None, str]:
        if "." in full_name:
            parts = full_name.rsplit(".", maxsplit=1)
            scope = parts[0]
            name = parts[1]
            if "." in name:
                raise ValueError("Symbol name must not contain '.' after normalization.")
            return scope, name
        else:
            return None, full_name

    @property
    def name(self) -> str:
        return self._name

    @property
    def annotation(self) -> Any | None:
        return self._annotation

    @property
    def kind(self) -> SymbolKind:
        return self._kind

    @property
    def scope(self) -> str | None:
        return self._scope

    @property
    def qualified_name(self) -> str:
        if self._scope:
            return f"{self._scope}.{self.name}"
        return self.name

    def __str__(self):
        return self.qualified_name

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name!r}, kind={self.kind!r}, annotation={self.annotation!r}, scope={self._scope!r})"

    def accept(self, visitor: SymbolVisitor):
        visitor.visit(self)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.name == other.name and self.kind == other.kind and self.annotation == other.annotation and self.scope == other.scope

    def __ne__(self, other: object) -> bool:
        return not self == other

    def __hash__(self) -> int:
        return hash((self.name, self.kind, str(self.annotation), self.scope))


class SymbolVisitor:
    """Visitor pattern implementation for traversing symbol hierarchies."""
    
    def generic_visit(self, node: SymbolDescriptor):
        raise NotImplementedError(f"No visit_{snake_case(node.__class__.__name__)} method defined")

    def visit(self, node: SymbolDescriptor):
        method_name = f"visit_{snake_case(node.__class__.__name__)}"
        method = getattr(self, method_name, self.generic_visit)
        method(node)


class SymbolDictionnary(ABC, Generic[Symbol]):
    """Base container for storing symbols in a list-like collection."""

    _symbols: OrderedDict[str, Symbol]
    __slots__ = ("_symbols",)

    def __init__(self):
        self._symbols = OrderedDict()

    def add(self, symbol: Symbol, ignore_duplicate: bool = True) -> Symbol:
        name = symbol.qualified_name
        if name in self._symbols:
            if ignore_duplicate:
                return self._symbols[name]
            raise ValueError(f"Duplicate symbol: {name}")
        self._symbols[name] = symbol
        return symbol

    def remove(self, qualified_name: str) -> None:
        self._symbols.pop(qualified_name, None)

    def get(self, qualified_name: str) -> Symbol | None:
        return self._symbols.get(qualified_name)

    def has(self, qualified_name: str) -> bool:
        return qualified_name in self._symbols

    def all(self) -> list[Symbol]:
        return list(self._symbols.values())

    def clear(self) -> None:
        self._symbols.clear()

    def __iter__(self) -> Iterator[Symbol]:
        return iter(self._symbols.values())

    def __len__(self) -> int:
        return len(self._symbols)

    def __contains__(self, something: str | SymbolDescriptor) -> bool:
        qualified_name = something.qualified_name if isinstance(something, SymbolDescriptor) else something
        return qualified_name in self._symbols

    def __getitem__(self, qualified_name: str) -> Symbol:
        return self._symbols[qualified_name]

    def accept(self, visitor: SymbolVisitor):
        for symbol in self._symbols.values():
            symbol.accept(visitor)