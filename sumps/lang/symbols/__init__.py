"""
Symbol system for representing Python code structures.

This package provides a hierarchical symbol system for representing Python code elements
like modules, classes, functions, variables, and parameters. It supports both static
analysis and runtime symbol management.
"""

from .base import *
from .local import *
from .module import *
from .parameter import *
from .reference import *
from .statement import *

# Re-export parameter conversion functions for backward compatibility
from .parameter import _parameter_kind_to_literal, _parameter_literal_to_kind

__all__ = [
    # Base types and classes
    "SymbolKind",
    "ParameterKind", 
    "Empty",
    "SymbolDescriptor",
    "SymbolVisitor",
    "SymbolDictionnary",
    
    # Local symbols
    "LocalSymbol",
    "LocalSymbolTable",
    
    # Parameters
    "ParameterSymbol",
    "Parameters",
    "_parameter_kind_to_literal",
    "_parameter_literal_to_kind",
    
    # Statements
    "Statement",
    "Statements",
    "FunctionSymbol",
    "VariableSymbol",
    "ClassSymbol",
    
    # References
    "SymbolReference",
    "SymbolTable",
    
    # Modules
    "ModuleSymbol",
]