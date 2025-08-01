from __future__ import annotations

from abc import ABC
from collections.abc import Iterator
from inspect import Signature
from typing import Any, cast

from .base import Empty, SymbolDescriptor, SymbolDictionnary, SymbolKind, SymbolVisitor
from .parameter import ParameterSymbol, Parameters

__all__ = ["Statement", "Statements", "FunctionSymbol", "VariableSymbol", "ClassSymbol"]


class Statement(SymbolDescriptor, ABC):
    """Abstract base class for code statements with body text."""

    __slots__ = SymbolDescriptor.__slots__ + ("body",)

    def __init__(self, name: str, body: str, kind: SymbolKind, annotation: Any | None = Empty) -> None:
        super().__init__(name=name, kind=kind, annotation=annotation)
        self.body: str = body

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"name={self._name!r}, kind={self.kind!r}, body={self.body!r}, "
            f"annotation={self._annotation!r}, scope={self._scope!r})"
        )


class Statements(SymbolDictionnary[Statement]):
    """Container for statement symbols with type-specific lookup methods."""
    
    def __init__(self):
        super().__init__()

    def get_symbol(self, name: str) -> Statement | None:
        """Get a statement by name."""
        return next((s for s in self._symbols.values() if s.name == name), None)

    def has_symbol(self, name: str) -> bool:
        """Check if a statement exists by name."""
        return self.has(name) is not None

    def get_symbols_by_type(self, symbol_type: SymbolKind) -> list[Statement]:
        """Get all statements of a specific type."""
        return [stmt for stmt in self._symbols.values() if stmt.kind == symbol_type]

    def get_variable(self, name: str) -> VariableSymbol | None:
        """Get a variable statement by name."""
        return next((cast(VariableSymbol, s) for s in self._symbols.values() if s.kind == "variable" and s.name == name), None)

    def get_function(self, name: str) -> FunctionSymbol | None:
        """Get a function statement by name."""
        return next((cast(FunctionSymbol, s) for s in self._symbols.values() if s.kind == "function" and s.name == name), None)

    def get_class(self, name: str) -> ClassSymbol | None:
        """Get a class statement by name."""
        return next((cast(ClassSymbol, s) for s in self._symbols.values() if s.kind == "class" and s.name == name), None)


class FunctionSymbol(Statement):
    """Represents a function, including its parameters and return type."""

    __slots__ = Statement.__slots__ + ("_parameters", "return_annotation", "is_async")

    def __init__(
        self,
        name: str,
        *,
        parameters: list[ParameterSymbol] | None = None,
        return_annotation: Any | None = Empty,
        body: str = "",
        is_async: bool = False,
    ):
        self._parameters: Parameters = Parameters()
        if parameters:
            for p in parameters:
                self._parameters.add(p)
        self.return_annotation: Any | None = return_annotation
        self.is_async: bool = is_async
        super().__init__(name=name, kind="function", annotation=return_annotation, body=body)

    def __str__(self) -> str:
        prefix = "async " if self.is_async else ""
        return f"{prefix}def {self.name}{self.get_signature()}"

    def get_signature(self) -> Signature:
        """Convert function symbol to inspect.Signature object."""
        return Signature(
            [param.to_inspect_parameter() for param in self._parameters],
            return_annotation=self.return_annotation if self.return_annotation is not Empty else Signature.empty,
        )

    @classmethod
    def from_signature(
        cls,
        name: str,
        signature: Signature,
        *,
        is_async: bool = False,
        body: str = "",
    ) -> FunctionSymbol:
        """Create FunctionSymbol from inspect.Signature object."""
        return cls(
            name=name,
            parameters=[ParameterSymbol.from_inspect_parameter(param=param) for param in signature.parameters.values()],
            return_annotation=signature.return_annotation if signature.return_annotation is not Signature.empty else Empty,
            is_async=is_async,
            body=body,
        )

    @property
    def parameters(self) -> Parameters:
        return self._parameters

    def __iter__(self) -> Iterator[ParameterSymbol]:
        """Allows iteration over parameter symbols."""
        return iter(self._parameters)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"name={self.name!r}, parameters={self.parameters!r}, "
            f"annotation={self.annotation!r}, scope={self.scope!r})"
        )

    def traverse_children(self, visitor: SymbolVisitor):
        self.parameters.accept(visitor)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FunctionSymbol):
            return NotImplemented
        return (
            self.name == other.name
            and self.parameters == other.parameters
            and self.return_annotation == other.return_annotation
            and self.is_async == other.is_async
            and self.scope == other.scope
        )


class VariableSymbol(Statement):
    """Represents a variable declaration with type annotation."""
    
    __slots__ = Statement.__slots__ + ("_value",)

    def __init__(self, name: str, *, annotation: Any | None = Empty, body: str = ""):
        super().__init__(name=name, kind="variable", annotation=annotation, body=body)

    def __str__(self) -> str:
        return f"{self.name}: {self.annotation if self.annotation is not Empty else 'Any'} = {self.body}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r}, annotation={self.annotation!r}, scope={self.scope!r}), body={self.body!r}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, VariableSymbol):
            return NotImplemented
        return (
            self.name == other.name
            and self.annotation == other.annotation
            and self.scope == other.scope
            and self.body == other.body
        )


class ClassSymbol(Statement):
    """Represents a class symbol with optional base classes and decorators."""

    __slots__ = Statement.__slots__ + ("_bases", "_decorators")

    def __init__(
        self, name: str, *, bases: list[str] | None = None, decorators: list[str] | None = None, annotation: Any | None = Empty, body: str
    ):
        super().__init__(name=name, kind="class", annotation=annotation, body=body)
        self._bases: list[str] = bases or []
        self._decorators: list[str] = decorators or []

    @property
    def bases(self) -> list[str]:
        return self._bases

    @property
    def decorators(self) -> list[str]:
        return self._decorators

    def add_base(self, base: str) -> None:
        self._bases.append(base)

    def add_decorator(self, decorator: str) -> None:
        self._decorators.append(decorator)

    def __str__(self) -> str:
        bases_str = f"({', '.join(self._bases)})" if self._bases else ""
        return f"class {self.name}{bases_str}"

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"name={self.name!r}, bases={self._bases!r}, decorators={self._decorators!r}, "
            f"annotation={self.annotation!r}, scope={self.scope!r})"
            f"body={self.body!r}"
        )