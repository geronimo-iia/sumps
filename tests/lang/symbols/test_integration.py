"""Integration tests for the symbols package to verify cross-module functionality."""

from sumps.lang.symbols import (
    ClassSymbol,
    FunctionSymbol,
    ModuleSymbol,
    ParameterSymbol,
    VariableSymbol,
)


class TestSymbolIntegration:
    def test_basic_integration(self):
        """Test basic integration between different symbol types."""
        func = FunctionSymbol(name="my_func", parameters=[], return_annotation="int")
        assert func.name == "my_func"
        assert func.return_annotation == "int"
        assert func.parameters.all() == []

    def test_function_with_parameters(self):
        """Test function symbol with parameters."""
        params = [ParameterSymbol(name="x", annotation="int"), ParameterSymbol(name="y", annotation="float")]
        func = FunctionSymbol(name="compute", parameters=params, return_annotation="float")
        assert len(func.parameters) == 2
        assert func.parameters["x"].name == "x"
        assert func.parameters["y"].annotation == "float"

    def test_variable_creation(self):
        """Test variable symbol creation."""
        var = VariableSymbol(name="counter", annotation="int", body="42")
        assert var.name == "counter"
        assert var.annotation == "int"
        assert var.body == "42"

    def test_class_inheritance_structure(self):
        """Test class symbol with inheritance."""
        derived = ClassSymbol(name="Dog", bases=["Animal"], body="pass")
        assert derived.name == "Dog"
        assert derived.bases == ["Animal"]

    def test_module_with_statements(self):
        """Test module symbol containing various statements."""
        module = ModuleSymbol(name="test_module")
        
        # Add a function
        func = FunctionSymbol("test_func", return_annotation="int")
        module.statements.add(func)
        
        # Add a class
        cls = ClassSymbol("TestClass", body="pass")
        module.statements.add(cls)
        
        # Add a variable
        var = VariableSymbol("test_var", body="42")
        module.statements.add(var)
        
        assert len(module.statements) == 3
        assert module.statements.get_function("test_func") == func
        assert module.statements.get_class("TestClass") == cls
        assert module.statements.get_variable("test_var") == var