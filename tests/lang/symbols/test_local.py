import pytest

from sumps.lang.symbols.local import LocalSymbol, LocalSymbolTable, _classify_object


class TestClassifyObject:
    def test_literal_types(self):
        assert _classify_object(123) == "variable"
        assert _classify_object(3.14) == "variable"
        assert _classify_object("hello") == "variable"
        assert _classify_object(True) == "variable"
        assert _classify_object(None) == "variable"

    def test_collections(self):
        assert _classify_object([1, 2, 3]) == "variable"
        assert _classify_object((1, 2)) == "variable"
        assert _classify_object({"a": 1}) == "variable"
        assert _classify_object({1, 2, 3}) == "variable"

    def test_function(self):
        def test_func():
            pass

        assert _classify_object(test_func) == "function"
        assert _classify_object(lambda x: x) == "function"

    def test_object_instance(self):
        class MyClass:
            def __init__(self):
                self.value = 1

        instance = MyClass()
        assert _classify_object(instance) == "variable"
        assert _classify_object(MyClass) == "class"


class TestLocalSymbol:
    def test_constructor_basic(self):
        symbol = LocalSymbol("x", reference=42)
        assert symbol.name == "x"
        assert symbol.annotation is int
        assert symbol.reference == 42
        
    def test_constructor_full(self):
        symbol = LocalSymbol("x", 42, annotation="int")
        assert symbol.name == "x"
        assert symbol.annotation == "int"
        assert symbol.reference == 42

    def test_equality_same(self):
        a = LocalSymbol("x", "int", 1)
        b = LocalSymbol("x", "int", 1)
        assert a == b

    def test_equality_different_name(self):
        a = LocalSymbol("x", "int", 1)
        b = LocalSymbol("y", "int", 1)
        assert a != b

    def test_equality_different_type(self):
        a = LocalSymbol("x", "int", 1)
        b = LocalSymbol("x", "str", 1)
        assert a != b

    def test_equality_different_value(self):
        a = LocalSymbol("x", "int", 1)
        b = LocalSymbol("x", "int", 2)
        assert a != b

    def test_equality_other_type(self):
        symbol = LocalSymbol("x", "int", 1)
        assert symbol != 123

    def test_repr_output(self):
        symbol = LocalSymbol("x", "int", 1)
        expected = "LocalSymbol(name='x', kind='variable', annotation=1, scope=None, weak_ref=False, reference='int')"
        assert repr(symbol) == expected


class TestLocalSymbolTable:
    def test_add_class(self):
        table = LocalSymbolTable()
        
        class TestClass:
            pass
        
        symbol = table.add_class(TestClass)
        assert symbol.name == "TestClass"
        assert symbol.kind == "class"

    def test_add_function(self):
        table = LocalSymbolTable()
        
        def test_func():
            pass
        
        symbol = table.add_function(test_func)
        assert symbol.name == "test_func"
        assert symbol.kind == "function"

    def test_add_variable(self):
        table = LocalSymbolTable()
        
        class TestObj:
            pass
        
        obj = TestObj()
        symbol = table.add_variable("test_var", obj)
        assert symbol.name == "test_var"
        assert symbol.kind == "variable"