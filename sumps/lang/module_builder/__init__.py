"""
Module builder package for dynamic Python module creation.

This package provides tools for building, executing, and managing dynamic Python modules
from symbol definitions. It includes code generation, environment setup, and module
lifecycle management.
"""

from .builder import *
from .dynamic import *
from .environment import *
from .visitor import *

# Apply singleton pattern to DynamicModuleManager
from ..singleton import singleton

DynamicModuleManager = singleton(DynamicModuleManager)

__all__ = [
    # Builder
    "ModuleBuilder",
    
    # Dynamic modules
    "DynamicModule", 
    "DynamicModuleManager",
    
    # Environment
    "GlobalEnvironmentBuilder",
    
    # Visitor
    "CodeGeneratorVisitor",
]