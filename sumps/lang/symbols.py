from __future__ import annotations

import re
from importlib import import_module
from inspect import Parameter as _Parameter
from inspect import Signature, _ParameterKind
from io import StringIO, TextIOBase
from typing import Any, Literal

from msgspec import Struct, field

from .factory import factory
from .registry import Dictionary
from .types import get_builtin_type_names

__all__ = [
    "Symbol",
    "Symbols",
    "Statement",
    "Statements",
    "ModuleSpecification",
    "Module",
    "StatementType",
    "ParameterKind",
    "Parameter",
    "FunctionStatement",
    "Encoder",
]


class Symbol(Struct):
    name: str
    module: str | None = None
    annotation: str | type[Any] | None = None

    def __post_init__(self):
        if "." in self.name:
            raise RuntimeError(f"symbol {self.name} should not contains dot character.")

    @classmethod
    def from_qualified_name(cls, name: str) -> Symbol:
        index = name.rfind(".")
        if index < 0:
            return Symbol(name=name)
        return Symbol(name=name[index + 1 :], module=name[0:index])

    def qualified_name(self) -> str:
        return f"{self.module}.{self.name}"

    def __str__(self):
        return self.qualified_name()

    def __repr__(self):
        return f"{self.qualified_name()}: {self.annotation}" if self.annotation else self.qualified_name()


class Symbols(Dictionary[Symbol]):
    def group_per_module(self) -> dict[str, str]:
        grouped_dict = {}
        for symbol in self.all():
            if symbol.module not in grouped_dict:
                grouped_dict[symbol.module] = [symbol.name]
            else:
                grouped_dict[symbol.module].append(symbol.name)
        return grouped_dict


type StatementType = Literal["parameter", "variable", "function", "class"]


class Statement(Symbol, kw_only=True):
    body: str = ""
    type: StatementType | None = None
    _module: Module | None = None

    def encode(self, output: Encoder):
        output.comment(f"name: {self.name}").comment(f"kind: {self.type}").write_lines(self.body).cr().cr()

    def register(self, module: Module) -> Module:
        """Register this statement."""
        if self._module:
            raise RuntimeError(
                f"Statement {self.name} should not bed registered in two module {self._module.name} and {module.name}"
            )
        self._module = module
        if module.statements.exists(name=self.name):
            raise RuntimeError(f"Statement {self.name} is ever registered in module {self._module.name}")
        module.statements.add(item=self)
        return module


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


class Parameter(Symbol, kw_only=True):
    default: Any = None
    kind: ParameterKind = "positional or keyword"

    def __post_init__(self):
        self.module = None


class Parameters(Dictionary[Parameter]):
    pass


class FunctionStatement(Statement, kw_only=True, tag=True, tag_field="_class"):
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

    def register(self, module: Module) -> Module:
        """Add a function statement.

        Analyse function signature and add ad hoc import if needed.
        """

        module = super().register(module=module)

        builtin_type_names = get_builtin_type_names()

        def _analyze_annotation(annotation):
            s = re.findall("'([^']*)'", repr(annotation))
            if len(s) > 0:
                _qualified_name = s[0]
                if _qualified_name not in builtin_type_names:
                    module.specification.add_symbol(qualified_name=_qualified_name)

        signature = self.signature()

        # import type of parameters
        for param in signature.parameters:
            _analyze_annotation(signature.parameters[param].annotation)

        # import return type
        if signature.return_annotation != Signature.empty:
            _analyze_annotation(signature.return_annotation)

        return module


class Statements(Dictionary[Statement]):
    def encode(self, output: Encoder):
        for statement in self.all():
            statement.encode(output=output)


class ModuleSpecification(Struct):
    modules: Symbols = field(default_factory=factory(Symbols))
    symbols: Symbols = field(default_factory=factory(Symbols))

    def __post_init__(self):
        self.add_symbol(qualified_name="__future__.annotations")

    def get_all_modules(self) -> set[str]:
        """Returns all specified modules."""
        return {m.qualified_name() for m in self.modules.all()}.union(
            {m.module for m in self.symbols.all() if m.module}
        )

    def add_module(self, qualified_name: str) -> ModuleSpecification:
        self.modules.add(Symbol.from_qualified_name(name=qualified_name))
        return self

    def add_symbol(self, qualified_name: str) -> ModuleSpecification:
        symbol = Symbol.from_qualified_name(name=qualified_name)
        if not symbol.module:
            raise RuntimeError(f"{symbol} is not a qualified symbol")
        self.symbols.add(symbol)
        return self

    def exists(self, name: str) -> bool:
        return self.modules.exists(name=name) or self.symbols.exists(name=name)

    def encode(self, output: Encoder):
        # import module
        for m in self.modules.all():
            output.write(f"import {m.qualified_name()}")

        # import symbols
        for key, value in self.symbols.group_per_module().items():
            if len(value) > 1:
                output.write(f"from {key} import ({','.join(value)})")
            else:
                output.write(f"from {key} import {value[0]}")

        output.cr()


class Module(Symbol, kw_only=True):
    specification: ModuleSpecification = field(default_factory=factory(ModuleSpecification))
    statements: Statements = field(default_factory=factory(Statements))

    def encodes(self) -> str:
        encoder = Encoder.encoder()
        self.encode(output=encoder)
        return encoder.getvalue()

    def encode(self, output: Encoder):
        output.comment(f"name: {self.name}")

        self.specification.encode(output=output)

        all = [f'"{spec.name}"' for spec in self.statements.filter(visibility="public")]
        if all:
            output.write("__all__ = [" + ", ".join(all) + "]").cr()

        output.cr()

        self.statements.encode(output=output)

    def add_class_reference(self, cls: type[Any]):
        """Add a class reference."""
        module = cls.__module__
        if module != "builtins":
            self.specification.symbols.add(item=Symbol(name=cls.__qualname__, module=module))

    # def add_function(self, function: FunctionStatement):
    #     """Add a function statement.

    #     Analyse function signature and add ad hoc import if needed.
    #     """

    #     self.statements.add(item=function)

    #     builtin_type_names = get_builtin_type_names()

    #     def _analyze_annotation(annotation):
    #         s = re.findall("'([^']*)'", repr(annotation))
    #         if len(s) > 0:
    #             _qualified_name = s[0]
    #             if _qualified_name not in builtin_type_names:
    #                 self.specification.add_symbol(qualified_name=_qualified_name)

    #     signature = function.signature()

    #     # import type of parameters
    #     for param in signature.parameters:
    #         _analyze_annotation(signature.parameters[param].annotation)

    #     # import return type
    #     if signature.return_annotation != Signature.empty:
    #         _analyze_annotation(signature.return_annotation)

    def import_module(self, locals: dict[str, Any] | None = None) -> dict[str, Any]:
        """Import this module."""

        # prepare global definition
        _global = {**globals()}
        for module_name in self.specification.get_all_modules():
            # import target module
            m = import_module(module_name)
            _global[module_name] = m
            # import root module
            if "." in module_name:
                root_module = module_name[0 : module_name.find(".")]
                m = import_module(root_module)
                _global[m.__name__] = m

        # add locals if any
        if locals:
            for key, value in locals.items():
                _global[key] = value

        # load symbol
        for symbol in self.specification.symbols.all():
            assert symbol.module
            if not symbol.module.startswith("__"):
                m = import_module(symbol.module)
                _global[symbol.name] = getattr(m, symbol.name)

        _locals = {}
        exec(self.encodes(), _global, _locals)
        return _locals


class Encoder:
    def __init__(self, output: TextIOBase, level: int = 0):
        self.output = output
        self.level = level

    def write(self, line: str) -> Encoder:
        self.output.write(f"{' ' * 4 * self.level}{line}\n")
        return self

    def __iadd__(self, line: str) -> Encoder:
        self.write(line)
        return self

    def comment(self, message) -> Encoder:
        self.write(f"#{message}")
        return self

    def indent(self) -> Encoder:
        self.level += 1
        return self

    def outdent(self) -> Encoder:
        self.level -= 1
        if self.level < 0:
            self.level = 0
        return self

    def write_lines(self, body: str) -> Encoder:
        for line in body.split("\n"):
            self.write(line)
        return self

    def add_statement(self, statement: Statement) -> Encoder:
        return self.indent().comment(repr(statement)).write_lines(body=statement.body).outdent()

    def cr(self) -> Encoder:
        self.output.write("\n")
        return self

    @classmethod
    def encoder(cls) -> Encoder:
        return Encoder(output=StringIO())

    def getvalue(self) -> str:
        return self.output.getvalue() if isinstance(self.output, StringIO) else ""
