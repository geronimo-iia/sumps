from io import StringIO

import pytest

from sumps.lang.module_builder import CodeGeneratorVisitor
from sumps.lang.symbols import ClassSymbol, FunctionSymbol, SymbolReference, VariableSymbol


@pytest.fixture
def visitor():
    output = StringIO()
    return CodeGeneratorVisitor(output), output


def test_visit_symbol_reference(visitor):
    visitor_obj, output = visitor
    ref = SymbolReference(name="os")
    visitor_obj.visit_symbol_reference(ref)
    assert output.getvalue() == "import os\n"


def test_visit_symbol_reference_with_alias(visitor):
    visitor_obj, output = visitor
    ref = SymbolReference(name="os", alias="operating_system")
    visitor_obj.visit_symbol_reference(ref)
    assert output.getvalue() == "import os as operating_system\n"


def test_visit_function_symbol(visitor):
    visitor_obj, output = visitor
    func = FunctionSymbol(name="test_func", body="return 42")
    visitor_obj.visit_function_symbol(func)
    expected = "def test_func():\n    return 42\n"
    assert output.getvalue() == expected


def test_visit_class_symbol(visitor):
    visitor_obj, output = visitor
    cls = ClassSymbol(name="TestClass", body="pass")
    visitor_obj.visit_class_symbol(cls)
    expected = "class TestClass:\n    pass\n"
    assert output.getvalue() == expected


def test_visit_variable_symbol(visitor):
    visitor_obj, output = visitor
    var = VariableSymbol(name="x", body="42")
    visitor_obj.visit_variable_symbol(var)
    assert output.getvalue() == "x = 42\n"
