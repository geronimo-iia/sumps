from __future__ import annotations

import builtins
from functools import lru_cache
from io import TextIOBase

from ..symbols import ClassSymbol, FunctionSymbol, ModuleSymbol, ParameterSymbol, SymbolVisitor, VariableSymbol

__all__ = ["CodeGeneratorVisitor"]


@lru_cache
def _get_builtin_type_names() -> list[str]:
    """returns a list of builtin type name."""
    return [getattr(builtins, d).__name__ for d in dir(builtins) if isinstance(getattr(builtins, d), type)]


class CodeGeneratorVisitor(SymbolVisitor):
    """Generates Python code from symbol descriptors with proper indentation."""

    __slots__ = ("output", "_level")

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

    def visit_symbol_reference(self, node):
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
        from ..symbols import Empty
        ann = f": {node.annotation}" if node.annotation is not Empty else ""
        self._write_line(f"{node.name}{ann} = {node.body or 'None'}")

    def visit_parameter_symbol(self, node: ParameterSymbol):
        # Parameters are included in FunctionSymbol signature; nothing to emit here.
        return

    def generic_visit(self, node):
        pass