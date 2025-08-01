# Ensure forward compatibility for type annotation
from __future__ import annotations

import uuid

# Imports for abstract base classes, type hinting, and introspection
from abc import ABC
from collections import OrderedDict
from collections.abc import Iterator
from inspect import Parameter, Signature, _ParameterKind, isbuiltin, isclass, isfunction, ismethod, ismodule
from types import ModuleType
from typing import Any, Generic, Literal, TypeVar, cast
from weakref import ref

from .stringcase import snake_case

__all__ = [
    "SymbolDescriptor",
    "SymbolKind",
    "Empty",
    "LocalSymbol",
    "LocalSymbolTable",
    "Statement",
    "Statements",
    "ParameterKind",
    "ParameterSymbol",
    "Parameters",
    "FunctionSymbol",
    "VariableSymbol",
    "ClassSymbol",
    "SymbolReference",
    "SymbolTable",
    "ModuleSymbol",
]

# Enumerates the possible types of symbols
SymbolKind = Literal["variable", "function", "class", "parameter", "module", "import"]

# ParameterKind act as a public interface of _ParameterKind definition.
ParameterKind = Literal[
    "POSITIONAL_ONLY",
    "POSITIONAL_OR_KEYWORD",
    "VAR_POSITIONAL",
    "KEYWORD_ONLY",
    "VAR_KEYWORD",
]

# Type variables
Symbol = TypeVar("Symbol", bound="SymbolDescriptor")
S = TypeVar("S", bound="Statement")


# Private helper functions
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


def _get_full_class_name(cls):
    """Get the full qualified class name including module."""
    return f"{cls.__module__}.{cls.__qualname__}"


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
            # never reached
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
            # never reached
            raise ValueError(f"Unknown kind string: {kind_str}")


class Empty:
    """Marker object to indicate an intentionally 'empty' value that is not None."""

    __slots__ = ()

    def __repr__(self):
        return "<Empty>"

    def __bool__(self):
        return False


class SymbolDescriptor(ABC):
    """
    Abstract base class representing a generic symbol with metadata.
    Includes name, scope, kind, and optional type annotation.
    """

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
        """
        Splits a dotted name (e.g. 'package.module.Class') into:
        - scope: the part before the last dot (e.g. 'package.module')
        - name: the last part (e.g. 'Class')
        """
        if "." in full_name:
            parts = full_name.rsplit(".", maxsplit=1)
            scope = parts[0]
            name = parts[1]
            if "." in name:
                # Defensive: name should not contain dots
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
        """Returns the full qualified name (e.g., 'scope.name' or just 'name')."""
        if self._scope:
            return f"{self._scope}.{self.name}"
        return self.name

    def __str__(self):
        return self.qualified_name

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name!r}, kind={self.kind!r}, annotation={self.annotation!r}, scope={self._scope!r})"

    def accept(self, visitor: SymbolVisitor):
        """Dispatch to the appropriate visitor method."""
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
        """Dispatch to the appropriate visit method based on node type.
        
        Examples: FunctionSymbol -> visit_function_symbol, LocalSymbol -> visit_local_symbol
        """
        method_name = f"visit_{snake_case(node.__class__.__name__)}"
        method = getattr(self, method_name, self.generic_visit)
        method(node)


class SymbolDictionnary(ABC, Generic[Symbol]):
    """Base container for storing symbols in a list-like collection."""

    _symbols: OrderedDict[str, Symbol]

    __slots__ = ("_symbols",)

    def __init__(self):
        self._symbols = OrderedDict()

    def add(self, symbol: Symbol, ignore_duplicate:bool=True) -> Symbol:
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


class LocalSymbol(SymbolDescriptor):
    """
    Represents a runtime-local symbol, with an actual object reference (possibly weak).
    """

    _reference: Any  # The Python object this symbol refers to

    __slots__ = SymbolDescriptor.__slots__ + ("_ref", "_weak")

    def __init__(self, name: str, reference: Any, annotation: Any | None = Empty) -> None:
        if reference is None:
            raise ValueError("LocalSymbol must have a reference.")

        # Deduce annotation if not explicitly given
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
        # Use id() for reference to avoid issues with unhashable objects
        return hash((self.name, self.kind, str(self.annotation), self.scope, id(self.reference)))

class LocalSymbolTable(SymbolDictionnary[LocalSymbol]):
    """Symbol table for runtime-local symbols with object references."""

    def add(self, symbol: LocalSymbol, ignore_duplicate:bool=True):
        """Add a local symbol to the table."""
        if symbol.kind not in ("variable", "function", "class"):
            raise ValueError(f"Expected a variable or function or class, got a {symbol.kind}")
        
        return super().add(symbol, ignore_duplicate=ignore_duplicate)
        

    def add_class(self, cls: type[Any], ignore_duplicate:bool=True) -> LocalSymbol:
        """Add a class to the symbol table."""
        module = cls.__module__
        if module.startswith("builtins"):
            raise RuntimeWarning("You shouldnt reference builtins module")
        
        #symbol = LocalSymbol(name=_get_full_class_name(cls), reference=cls)
        
        return self.add(symbol=LocalSymbol(name=cls.__qualname__, reference=cls), ignore_duplicate=ignore_duplicate)

    def add_function(self, func: Any, ignore_duplicate:bool=True, support_lambda: bool = True) -> LocalSymbol:
        """Add a function to the symbol table.
        
        Args:
            func: The callable function to add
            ignore_duplicate: If True, silently ignore duplicate functions
            support_lambda: If True, allow lambda functions with generated names
            
        Returns:
            LocalSymbol representing the added function
            
        Raises:
            ValueError: If func is not callable
            RuntimeWarning: If func is from builtins module or is lambda when not supported
        """

        if not callable(func):
            raise ValueError(f"Expected a callable, got a {type(func)}")
        
        module = func.__module__

        if module == "builtins":
            raise RuntimeWarning("You shouldnt reference builtins module")
        
        if _is_lambda(func):
            if not support_lambda:
                raise RuntimeWarning("You shouldnt reference lambda functions")
            func.__name__= f"lambda_{uuid.uuid4().hex}"
        
        return self.add(symbol=LocalSymbol(name=_get_function_name(func), reference=func), ignore_duplicate=ignore_duplicate)
    

    def add_variable(self, name: str, value: Any) -> LocalSymbol:
        """Add a variable to the symbol table."""
        module = value.__module__
        if module == "builtins":
            raise RuntimeWarning("You shouldnt reference builtins module")
        return self.add(LocalSymbol(name=name, reference=value))


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


class ParameterSymbol(SymbolDescriptor):
    """
    Represents a function or method parameter, including its name, annotation, kind, and default value.
    Wraps around Python's `inspect.Parameter`.
    """

    __slots__ = SymbolDescriptor.__slots__ + (
        "parameter_kind",
        "default",
    )

    def __init__(
        self, name: str, parameter_kind: ParameterKind = "POSITIONAL_OR_KEYWORD", *, annotation: Any = Empty, default: Any = Empty
    ) -> None:
        super().__init__(name=name, kind="parameter", annotation=annotation)
        self.parameter_kind: ParameterKind = parameter_kind
        self.default: Any = default

        if self.parameter_kind in ("VAR_POSITIONAL", "VAR_KEYWORD"): # variadic positional parameters cannot have default values
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
    """Container for functiosymboln parameter symbols."""
    
    def add(self, symbol: ParameterSymbol, ignore_duplicate:bool=False):
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

class FunctionSymbol(Statement):
    """
    Represents a function, including its parameters and return type.
    Extracts parameter symbols from the function signature.
    """

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
        *,  # everything after this must be passed as keyword arguments.
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
    """
    Represents a class symbol with optional contained class-level functions (methods), base classes and decorators.
    """

    __slots__ = Statement.__slots__ + (
        "_bases",
        "_decorators",
    )  # '_methods'

    def __init__(
        self, name: str, *, bases: list[str] | None = None, decorators: list[str] | None = None, annotation: Any | None = Empty, body: str
    ):
        super().__init__(name=name, kind="class", annotation=annotation, body=body)
        self._bases: list[str] = bases or []
        self._decorators: list[str] = decorators or []
        # self._methods= []
        # self._attributes = []

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

    # @property
    # def methods(self) -> list[FunctionSymbol]:
    #     return self._methods

    # def add_method(self, method: FunctionSymbol) -> None:
    #     """Adds a function symbol representing a method of the class."""
    #     if len(method.parameters) == 0 or method.parameters[0].name != "self":
    #         raise ValueError("Method must have 'self' as first parameter")
    #     self._methods.append(method)

    # def traverse_children(self, visitor: SymbolVisitor):
    #     yield from self.methods.accept(visitor)


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

    def add(self, symbol: SymbolReference, ignore_duplicate:bool=True) -> SymbolReference:
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
        #print(f"adding {cls} {_get_full_class_name(cls)} {cls.__qualname__}")
        
        return self.add(symbol= SymbolReference(name=_get_full_class_name(cls), annotation=cls))

    def add_function(self, func: Any) -> SymbolReference:
        """Add a function reference."""
        module = func.__module__
        if module.startswith("builtins"):
            raise RuntimeWarning("You shouldnt reference builtins module")
        return self.add(SymbolReference(name=func.__qualname, annotation=type(func)))


class ModuleSymbol(SymbolDescriptor):
    """
    Represents a module with its top-level classes, functions, and optionally variables.
    """

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

    # def accept(self, visitor: SymbolVisitor):
    #     """Dispatch to the appropriate visitor method."""
    #     visitor.visit(self)

    def traverse_children(self, visitor: SymbolVisitor):
        """Visit all child symbols in the module."""
        # Visit references (imports)
        self.references.accept(visitor=visitor)

        # Visit top-level statements (functions, classes, variables)
        self.statements.accept(visitor=visitor)
