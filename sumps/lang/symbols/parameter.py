from __future__ import annotations

from inspect import Parameter, _ParameterKind
from typing import Any

from .base import Empty, ParameterKind, SymbolDescriptor, SymbolDictionnary

__all__ = ["ParameterSymbol", "Parameters"]


def _parameter_kind_to_literal(kind: _ParameterKind) -> ParameterKind:
    """Convert inspect.Parameter kind to literal string."""
    match kind:
        case Parameter.POSITIONAL_ONLY:
            return "POSITIONAL_ONLY"
        case Parameter.POSITIONAL_OR_KEYWORD:
            return "POSITIONAL_OR_KEYWORD"
        case Parameter.VAR_POSITIONAL:
            return "VAR_POSITIONAL"
        case Parameter.KEYWORD_ONLY:
            return "KEYWORD_ONLY"
        case Parameter.VAR_KEYWORD:
            return "VAR_KEYWORD"
        case _:
            raise ValueError(f"Unknown Parameter kind: {kind}")


def _parameter_literal_to_kind(kind_str: ParameterKind) -> _ParameterKind:
    """Convert literal string to inspect.Parameter kind."""
    match kind_str:
        case "POSITIONAL_ONLY":
            return Parameter.POSITIONAL_ONLY
        case "POSITIONAL_OR_KEYWORD":
            return Parameter.POSITIONAL_OR_KEYWORD
        case "VAR_POSITIONAL":
            return Parameter.VAR_POSITIONAL
        case "KEYWORD_ONLY":
            return Parameter.KEYWORD_ONLY
        case "VAR_KEYWORD":
            return Parameter.VAR_KEYWORD
        case _:
            raise ValueError(f"Unknown kind string: {kind_str}")


class ParameterSymbol(SymbolDescriptor):
    """Represents a function or method parameter."""

    __slots__ = SymbolDescriptor.__slots__ + ("parameter_kind", "default")

    def __init__(
        self, name: str, parameter_kind: ParameterKind = "POSITIONAL_OR_KEYWORD", *, annotation: Any = Empty, default: Any = Empty
    ) -> None:
        super().__init__(name=name, kind="parameter", annotation=annotation)
        self.parameter_kind: ParameterKind = parameter_kind
        self.default: Any = default

        if self.parameter_kind in ("VAR_POSITIONAL", "VAR_KEYWORD"):
            self.default = Empty

    def __repr__(self):
        return (
            f"ParameterSymbol(name={self.name!r}, parameter_kind={self.parameter_kind!r}, "
            f"default={self.default!r}, annotation={self.annotation!r}, scope={self.scope!r})"
        )

    def to_inspect_parameter(self) -> Parameter:
        return Parameter(
            name=self.name,
            kind=_parameter_literal_to_kind(self.parameter_kind),
            default=self.default if self.default is not Empty else Parameter.empty,
            annotation=self.annotation if self.annotation is not Empty else Parameter.empty,
        )

    @classmethod
    def from_inspect_parameter(cls, param: Parameter) -> ParameterSymbol:
        return cls(
            name=param.name,
            parameter_kind=_parameter_kind_to_literal(param.kind),
            default=param.default if param.default is not Parameter.empty else Empty,
            annotation=param.annotation if param.annotation is not Parameter.empty else Empty,
        )
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return (
            self.name == other.name
            and self.parameter_kind == other.parameter_kind
            and self.default == other.default
            and self.annotation == other.annotation
            and self.scope == other.scope
        )


class Parameters(SymbolDictionnary[ParameterSymbol]):
    """Container for function parameter symbols."""
    
    def add(self, symbol: ParameterSymbol, ignore_duplicate: bool = False):
        """Add a parameter symbol to the collection."""
        if symbol.kind != "parameter":
            raise ValueError(f"Expected a parameter, got a {symbol.kind}")
        return super().add(symbol, ignore_duplicate)

    def add_parameter(
        self, name: str, parameter_kind: ParameterKind = "POSITIONAL_OR_KEYWORD", *, annotation: Any = Empty, default: Any = Empty
    ) -> ParameterSymbol:
        """Create and add a parameter symbol."""
        parameter = ParameterSymbol(name=name, annotation=annotation, default=default, parameter_kind=parameter_kind)
        self.add(symbol=parameter)
        return parameter

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self._symbols == other._symbols