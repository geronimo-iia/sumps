from __future__ import annotations

import ast
import os
import re
from datetime import datetime
from importlib import import_module
from types import ModuleType
from typing import Any

from msgspec import Struct, field

from .encoder import Encoder
from .factory import factory
from .function import FunctionStatement, Signature
from .statement import Statements
from .symbol import Symbol, Symbols
from .types import get_builtin_type_names

__all__ = [
    "ModuleSpecification",
    "Module",
]


class ModuleImportSpecification(Struct):
    modules: Symbols = field(default_factory=factory(Symbols))
    symbols: Symbols = field(default_factory=factory(Symbols))

    def __post_init__(self):
        self.add_symbol(qualified_name="__future__.annotations")

    def get_all_modules(self) -> set[str]:
        """Returns all specified modules."""
        return {m.qualified_name() for m in self.modules.all()}.union(
            {m.module for m in self.symbols.all() if m.module}
        )

    def add_module(self, qualified_name: str) -> ModuleImportSpecification:
        self.modules.add(Symbol.from_qualified_name(name=qualified_name))
        return self

    def add_symbol(self, qualified_name: str) -> ModuleImportSpecification:
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

import builtins


class Module(Symbol):
    specification: ModuleImportSpecification = field(default_factory=factory(ModuleImportSpecification))
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

    def add_class_reference(self, cls: type[Any]) -> Module:
        """Add a class reference."""
        module = cls.__module__
        if module != "builtins":
            self.specification.symbols.add(item=Symbol(name=cls.__qualname__, module=module))
        return self

    def add_function(self, function: FunctionStatement) -> Module:
        if not self.statements.exists(name=function.name):
            register_function(module=self, function=function)
        return self

    def import_module(self, locals: dict[str, Any] | None = None) -> dict[str, Any]:
        """Import this module."""

        # prepare global definition
        _global = {**globals()}

        _global = {"__builtins__": __builtins__}
        # define only what you need (e.g. basic safe globals + injected modules/symbols).

        loaded_modules = {}
        for module_name in self.specification.get_all_modules():
            # import target module
            if module_name not in loaded_modules:
                m = import_module(module_name)
                loaded_modules[module_name] = m
                _global[module_name] = m

            m = import_module(module_name)
            _global[module_name] = m
            # import root module
            if "." in module_name:
                #root_module = module_name[0 : module_name.find(".")]
                root_name = module_name.split(".")[0]
                if root_name not in _global:
                    m_root = import_module(root_name)
                    _global[root_name] = m_root
                #m = import_module(root_module)
                #_global[m.__name__] = m

        # add locals if any
        if locals:
            for key, value in locals.items():
                _global[key] = value

        # load symbol
        for symbol in self.specification.symbols.all():
            assert symbol.module
            if not symbol.module.startswith("__"):
                m = import_module(symbol.module)
                try:
                    _global[symbol.name] = getattr(m, symbol.name)
                except AttributeError:
                    raise ImportError(f"Symbol '{symbol.name}' not found in module '{symbol.module}'")

        _locals = {}
        exec(self.encodes(), _global, _locals)
        return _locals

    def import_module2(self, locals: dict[str, Any] | None = None) -> ModuleType:
        """Import this module."""
        # Start with a minimal global environment
        _globals: dict[str, Any] = {"__builtins__": builtins}
        loaded_modules: dict[str, ModuleType] = {}
        
        # Step 1: Import all listed modules
        for module_name in self.specification.get_all_modules():
            if module_name not in loaded_modules:
                try:
                    mod = import_module(module_name)
                    _globals[module_name] = mod
                    loaded_modules[module_name] = mod
                except ImportError as e:
                    raise ImportError(f"Failed to import module '{module_name}': {e}")

            # Ensure root module is also accessible
            if "." in module_name:
                root_name = module_name.split(".")[0]
                if root_name not in _globals:
                    try:
                        root_mod = import_module(root_name)
                        _globals[root_name] = root_mod
                        loaded_modules[root_name] = root_mod
                    except ImportError as e:
                        raise ImportError(f"Failed to import root module '{root_name}': {e}")

        # Step 2: Inject user-provided locals (if any)
        if locals:
            for k, v in locals.items():
                _globals[k] = v

        
        # Step 3: Load specific symbols from modules
        for symbol in self.specification.symbols.all():
            if not symbol.module or symbol.module.startswith("__"):
                continue
            try:
                mod = loaded_modules.get(symbol.module)
                if not mod:
                    mod = import_module(symbol.module)
                    loaded_modules[symbol.module] = mod
                    _globals[symbol.module] = mod
                _globals[symbol.name] = getattr(mod, symbol.name)
            except Exception as e:
                raise ImportError(
                    f"Failed to load symbol '{symbol.name}' from module '{symbol.module}': {e}"
                )

        # Step 4: Parse and verify code
        code = self.encodes()
        try:
            ast.parse(code, filename=self.name)
        except SyntaxError as e:
            line = e.text.strip() if e.text else ''
            raise SyntaxError(
                f"SyntaxError in {self.name} at line {e.lineno}, column {e.offset}:\n"
                f"{code}\n"
                f"Message: {e.msg}"
            )

        # Step 5: Execute into a module
        dynamic_module = ModuleType(self.name)
        dynamic_module.__dict__.update(_globals)

        code = self.encodes()
        try:
            exec(code, dynamic_module.__dict__)
        except Exception as e:
            raise RuntimeError(f"Error during code execution: {e}\nCode:\n{code}")
        
        return dynamic_module
    

    # TODO transform this in debug function
    def dump_to_file(
        self,
        module: ModuleType,
        path: str,
        include_metadata: bool = True,
        encoding: str = "utf-8",
    ) -> str:
        """
        Dump the generated module source code to a .py file.

        Args:
            module: The dynamically generated module (from `load_as_module()`).
            path: The path to write to (e.g., 'my_module.py').
            include_metadata: If True, prepends autogenerated metadata.
            encoding: Encoding for the output file.

        Returns:
            The absolute file path written to.
        """
        code = self.encodes()

        lines = []

        if include_metadata:
            lines.append("# ===============================================")
            lines.append("# This file was auto-generated by ModuleBuilder.")
            lines.append(f"# Module name: {module.__name__}")
            lines.append(f"# Generated at: {datetime.utcnow().isoformat()} UTC")
            lines.append("# ===============================================")
            lines.append("")

            # Dump imported modules
            lines.append("# Referenced modules:")
            for modname in self.specification.get_all_modules():
                lines.append(f"#   - {modname}")
            lines.append("")

            # Dump imported symbols
            lines.append("# Referenced symbols:")
            for symbol in self.specification.symbols.all():
                if symbol.module:
                    lines.append(f"#   from {symbol.module} import {symbol.name}")
            lines.append("")

        lines.append(code)

        abs_path = os.path.abspath(path)
        with open(abs_path, "w", encoding=encoding) as f:
            f.write("\n".join(lines))

        return abs_path

def register_function(module: Module, function: FunctionStatement):
    """Add a function statement.

    Analyse function signature and add ad hoc import if needed.
    """

    module.statements.add(item=function)

    builtin_type_names = get_builtin_type_names()

    def _analyze_annotation(annotation):
        s = re.findall("'([^']*)'", repr(annotation))
        if len(s) > 0:
            _qualified_name = s[0]
            if _qualified_name not in builtin_type_names:
                module.specification.add_symbol(qualified_name=_qualified_name)

    signature = function.signature()

    # import type of parameters
    for param in signature.parameters:
        _analyze_annotation(signature.parameters[param].annotation)

    # import return type
    if signature.return_annotation != Signature.empty:
        _analyze_annotation(signature.return_annotation)
