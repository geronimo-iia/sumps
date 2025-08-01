"""
`module_builder` contains several classes that work together to dynamically build and manage Python modules:

- ModuleBuilder - The main class that builds dynamic Python modules from symbol definitions
- DynamicModule - A wrapper for dynamically created modules with unload capabilities
- DynamicModuleManager - A singleton manager for dynamic modules
- CodeGeneratorVisitor - Generates Python code from symbol descriptors
- GlobalEnvironmentBuilder - Builds global environments by importing modules

"""
from __future__ import annotations

import ast
import builtins
import logging
import re
import sys
import uuid
import weakref
from collections.abc import Callable
from datetime import datetime
from functools import lru_cache, wraps
from importlib import import_module, invalidate_caches
from inspect import Signature
from io import StringIO, TextIOBase
from types import MethodType, ModuleType
from typing import Any, TypeVar, cast

from .singleton import singleton
from .symbols import (
    ClassSymbol,
    Empty,
    FunctionSymbol,
    LocalSymbol,
    LocalSymbolTable,
    ModuleSymbol,
    ParameterSymbol,
    Statement,
    SymbolDescriptor,
    SymbolReference,
    SymbolVisitor,
    VariableSymbol,
)

_T = TypeVar("_T")
_FUNC = TypeVar("_FUNC", bound=Callable)

__all__ = ["ModuleBuilder", "DynamicModule", "DynamicModuleManager", "CodeGeneratorVisitor", "GlobalEnvironmentBuilder"]


@lru_cache
def _get_builtin_type_names() -> list[str]:
    """returns a list of builtin type name."""
    return [getattr(builtins, d).__name__ for d in dir(builtins) if isinstance(getattr(builtins, d), type)]


_BUILTINT_TYPE_NAMES = _get_builtin_type_names()

T = TypeVar("T", bound=TextIOBase)


class CodeGeneratorVisitor(SymbolVisitor):
    """Generates Python code from symbol descriptors with proper indentation."""

    __slots__ = (
        "output",
        "_indent",
    )

    def __init__(self, output: TextIOBase):
        self._level: int = 0
        self.output: TextIOBase = output

    def _write_line(self, content: str = ""):
        self.output.write(f"{' ' * 4 * self._level}{content}\n")

    def _write_lines(self, body: str):
        for line in body.split("\n"):
            self._write_line(line)

    def cr(self):
        self.output.write("\n")

    def _indent_text(self):
        self._level += 1

    def _outdent_text(self):
        self._level -= 1
        if self._level < 0:
            self._level = 0

    def visit_module_symbol(self, node: ModuleSymbol):
        if node.docstring:
            self._write_line(f'""" {node.docstring} """')
        node.traverse_children(visitor=self)
    
    def visit_module_builder(self, node: ModuleSymbol):
        return self.visit_module_symbol(node=node)

    def visit_symbol_reference(self, node: SymbolReference):
        if node.alias:
            self._write_line(f"import {node.name} as {node.alias}")
        else:
            self._write_line(f"import {node.name}")

    def visit_class_symbol(self, node: ClassSymbol):
        bases = f"({', '.join(node.bases)})" if node.bases else ""
        for decorator in node.decorators:
            self._write_line(f"@{decorator}")
        self._write_line(f"class {node.name}{bases}:")
        self._indent_text()
        self._write_lines(node.body)
        self._outdent_text()

    def visit_function_symbol(self, node: FunctionSymbol):
        prefix = "async " if node.is_async else ""
        sig = node.get_signature()
        params = str(sig)
        self._write_line(f"{prefix}def {node.name}{params}:")
        self._indent_text()
        self._write_lines(node.body.strip() or "pass")
        self._outdent_text()

    def visit_variable_symbol(self, node: VariableSymbol):
        ann = f": {node.annotation}" if node.annotation is not Empty else ""
        self._write_line(f"{node.name}{ann} = {node.body or 'None'}")

    def visit_parameter_symbol(self, node: ParameterSymbol):
        # Parameters are included in FunctionSymbol signature; nothing to emit here.
        return

    def generic_visit(self, node: SymbolDescriptor):
        pass


class GlobalEnvironmentBuilder(SymbolVisitor):
    """Builds a global environment by importing modules and setting up symbol references.

    Args:
        use_current_context: If True, initializes globals from current context, otherwise uses minimal builtins.
    """

    __slots__ = (
        "_globals",
        "_loaded_modules",
    )

    def __init__(self, use_current_context: bool = False):
        super().__init__()
        self._globals: dict[str, Any] = {**globals()} if use_current_context else {"__builtins__": builtins}
        self._loaded_modules: dict[str, ModuleType] = {}

    def build(self) -> dict[str, Any]:
        return self._globals

    def visit_symbol_reference(self, node: SymbolReference):
        module_name = node.scope if node.scope and node.name == "*" else node.qualified_name
        if module_name.startswith("__") or module_name.startswith("builtins"):
            # ignore private module
            return

        if module_name and module_name not in self._loaded_modules:
            try:
                mod = import_module(module_name)
                self._globals[module_name] = mod
                self._loaded_modules[module_name] = mod
            except ImportError as e:
                raise ImportError(f"Failed to import module '{module_name}': {e}") from e

            # Ensure root module is also accessible
            if "." in module_name:
                root_name = module_name.split(".")[0]
                if root_name not in self._globals:
                    try:
                        root_mod = import_module(root_name)
                        self._globals[root_name] = root_mod
                        self._loaded_modules[root_name] = root_mod
                    except ImportError as e:
                        raise ImportError(f"Failed to import root module '{root_name}': {e}") from e
            # set specific symbols from modules
            if node.name != "*" and node.name not in dir(mod):
                try:
                    self._globals[node.aliased_name] = getattr(self._globals[module_name], node.name)
                except Exception as e:
                    raise ImportError(f"Symbol '{node.name}' not found in module '{module_name}':  {e}") from e

    def visit_local_symbol(self, node: LocalSymbol):
        self._globals[node.qualified_name] = node.reference

    def generic_visit(self, node: SymbolDescriptor):
        pass


class ModuleBuilder(ModuleSymbol):
    """Builds dynamic Python modules from symbol definitions with code generation and execution."""

    _locals: LocalSymbolTable
    __slots__ = ModuleSymbol.__slots__ + ("_locals",)

    def __init__(self, name: str | None = None, docstring: str | None = None):
        self._locals = LocalSymbolTable()
        super().__init__(name=name if name else f"dynamic_{uuid.uuid4().hex}", docstring=docstring)

    @property
    def locals(self) -> LocalSymbolTable:
        return self._locals

    def _analyze_annotation(self, annotation: type[Any]) -> SymbolReference | None:
        """Analyse provided annotation and reference all necessary symbols."""
        if annotation is Signature.empty: # ignore empty marker ("inspect._empty")
            return None
        s = re.findall("'([^']*)'", repr(annotation))
        if len(s) > 0:
            _qualified_name = s[0]
            if _qualified_name not in _BUILTINT_TYPE_NAMES:
                return self.references.add(symbol=SymbolReference(name=_qualified_name))
        return None

    def add_statement(self, stmt: Statement) -> ModuleBuilder:
        """Adds a statement and analyzes its type annotations for imports."""
        statement = super().statements.add(stmt)
        # update symbol table reference if needed
        match statement.kind:
            case "class":
                # for now, add specific reference its done per user of module builder.
                pass
            case "function":
                function = cast(FunctionSymbol, statement)
                signature = function.get_signature()
                # import type of parameters
                for param in signature.parameters:
                    self._analyze_annotation(signature.parameters[param].annotation)
                # import return type
                if signature.return_annotation != Signature.empty:
                    self._analyze_annotation(signature.return_annotation)
            case _:
                pass
        return self

    def encodes(self, output: T) -> T:
        """Generates Python code from symbols and writes to output stream."""
        output.write(f"# Generated by {self.__class__.__name__} at {datetime.now().isoformat()}\n")
        visitor = CodeGeneratorVisitor(output=output)
        self.accept(visitor=visitor)
        return output

    def build(self, use_current_context: bool = False, store_in_sys_modules: bool = False, debug_logger: logging.Logger | None = None) -> DynamicModule:
        """Builds and executes the module, returning a DynamicModule instance.

        Args:
            use_current_context: If True, uses current globals for execution environment.
            store_in_sys_modules: If True, registers module in sys.modules for import access.
            debug_logger: If provided, logs generated code using this logger.
        """
        # Start with a minimal global environment
        global_visitor = GlobalEnvironmentBuilder(use_current_context=use_current_context)

        # Step 1: Import all listed symbol table
        self.references.accept(global_visitor)

        # Step 2: Inject user-provided locals (if any)
        self._locals.accept(global_visitor)

        # Step 3: Parse and verify code
        code = self.encodes(output=StringIO()).getvalue()
        try:
            ast.parse(code, filename=self.name)
        except SyntaxError as e:
            text = e.text.strip() if e.text else ""
            raise SyntaxError(f"SyntaxError in {self.name} at line {e.lineno}, column {e.offset}:\n{text}\n{code}\nMessage: {e.msg}") from e

        # Step 4: Execute into a module
        dynamic_module = ModuleType(self.qualified_name)
        dynamic_module.__dict__.update(global_visitor.build())
        try:
            if debug_logger:
                debug_logger.debug(f"Generated code for {self.name}:\n{code}")
            exec(code, dynamic_module.__dict__)
        except Exception as e:
            raise RuntimeError(f"Error during code execution: {e}\nCode:\n{code}") from e

        return DynamicModule(module=dynamic_module, store_in_sys_modules=store_in_sys_modules)


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

        raise AttributeError(f"Symbol '{name}' not found in module '{self.__name__} {dir(self._module)}")

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
    ) -> _FUNC:  # noqa: E501
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


@singleton
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
