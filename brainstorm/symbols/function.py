from __future__ import annotations

from inspect import Parameter as _Parameter
from inspect import Signature, _ParameterKind
from typing import Any, Literal

from msgspec import field

from ..registry import Dictionary
from .encoder import Encoder
from .factory import factory
from .statement import Statement
from .symbol import Symbol

__all__ = ["ParameterKind", "Parameter", "FunctionStatement", "Signature"]

type ParameterKind = Literal["positional-only", "positional or keyword", "keyword-only"]


def _kind_of_parameter(kind) -> ParameterKind:
    match kind:
        case _Parameter.POSITIONAL_ONLY:
            return "positional-only"
        case _Parameter.KEYWORD_ONLY:
            return "keyword-only"
        case _:
            return "positional or keyword"


def _parameter_of_kind(kind: ParameterKind) -> _ParameterKind:
    match kind:
        case "positional-only":
            return _Parameter.POSITIONAL_ONLY
        case "keyword-only":
            return _Parameter.KEYWORD_ONLY
        case _:
            return _Parameter.POSITIONAL_OR_KEYWORD


class Parameter(Symbol):
    default: Any = None
    kind: ParameterKind = "positional or keyword"

    def __post_init__(self):
        self.module = None


class Parameters(Dictionary[Parameter]):
    pass


class FunctionStatement(Statement):
    parameters: Parameters = field(default_factory=factory(Parameters))
    is_async: bool = False

    def __post_init__(self):
        self.type = "function"

    def add_parameter(
        self,
        name: str,
        annotation: type[Any] | None = None,
        default: Any = None,
        kind: ParameterKind = "positional or keyword",
    ) -> FunctionStatement:
        self.parameters.add(Parameter(name=name, annotation=annotation, default=default, kind=kind))
        return self

    def signature(self) -> Signature:
        return Signature(
            parameters=[
                _Parameter(name=p.name, kind=_parameter_of_kind(p.kind), annotation=p.annotation, default=p.default)
                for p in self.parameters.all()
            ],
            return_annotation=self.annotation,
        )

    def set_signature(self, sign: Signature):
        self.annotation = sign.return_annotation
        self.parameters = Parameters()
        for p in sign.parameters.values():
            self.parameters.add(
                Parameter(name=p.name, annotation=p.annotation, default=p.default, kind=_kind_of_parameter(p.kind))
            )

    def __repr__(self):
        return f"{self.qualified_name()}{str(self.signature())}"

    def encode(self, output: Encoder):
        prelude = "async def" if self.is_async else "def"
        output.comment(self.name).write(f"{prelude} {self.name}{self.signature()}:").indent().write_lines(
            body=self.body
        ).outdent().cr().cr()

    # def register(self, module: Module) -> Module:
    #     """Add a function statement.

    #     Analyse function signature and add ad hoc import if needed.
    #     """

    #     module = super().register(module=module)

    #     builtin_type_names = get_builtin_type_names()

    #     def _analyze_annotation(annotation):
    #         s = re.findall("'([^']*)'", repr(annotation))
    #         if len(s) > 0:
    #             _qualified_name = s[0]
    #             if _qualified_name not in builtin_type_names:
    #                 module.specification.add_symbol(qualified_name=_qualified_name)

    #     signature = self.signature()

    #     # import type of parameters
    #     for param in signature.parameters:
    #         _analyze_annotation(signature.parameters[param].annotation)

    #     # import return type
    #     if signature.return_annotation != Signature.empty:
    #         _analyze_annotation(signature.return_annotation)

    #     return module
