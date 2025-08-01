from __future__ import annotations

from typing import Any

from .base import Empty, SymbolDescriptor, SymbolVisitor
from .reference import SymbolTable
from .statement import Statements

__all__ = ["ModuleSymbol"]


class ModuleSymbol(SymbolDescriptor):
    """Represents a module with its top-level classes, functions, and optionally variables."""

    __slots__ = SymbolDescriptor.__slots__ + ("_docstring", "_references", "_statements")

    def __init__(
        self,
        name: str,
        *,
        docstring: str | None = None,
        annotation: Any | None = Empty,
    ):
        self._docstring: str | None = docstring
        self._statements: Statements = Statements()
        self._references: SymbolTable = SymbolTable()
        super().__init__(name=name, kind="module", annotation=annotation)

    @property
    def docstring(self) -> str | None:
        return self._docstring

    @property
    def references(self) -> SymbolTable:
        return self._references

    @property
    def statements(self) -> Statements:
        return self._statements

    def __str__(self) -> str:
        return f"module {self.qualified_name}"

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"name={self.name!r}, scope={self.scope!r}, docstring={self._docstring!r}, "
            f"statements={len(self._statements)})"
        )

    def traverse_children(self, visitor: SymbolVisitor):
        """Visit all child symbols in the module."""
        self.references.accept(visitor=visitor)
        self.statements.accept(visitor=visitor)