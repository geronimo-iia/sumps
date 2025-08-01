from __future__ import annotations

import builtins
from importlib import import_module
from types import ModuleType
from typing import Any

from ..symbols import LocalSymbol, SymbolDescriptor, SymbolReference, SymbolVisitor

__all__ = ["GlobalEnvironmentBuilder"]


class GlobalEnvironmentBuilder(SymbolVisitor):
    """Builds a global environment by importing modules and setting up symbol references.

    Args:
        use_current_context: If True, initializes globals from current context, otherwise uses minimal builtins.
    """

    __slots__ = ("_globals", "_loaded_modules")

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