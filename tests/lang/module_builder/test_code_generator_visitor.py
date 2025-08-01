from io import StringIO

from sumps.lang.module_builder import CodeGeneratorVisitor
from sumps.lang.symbols import ClassSymbol, FunctionSymbol, SymbolReference, VariableSymbol


class TestCodeGeneratorVisitor:
    def test_visit_symbol_reference(self):
        output = StringIO()
        visitor = CodeGeneratorVisitor(output)
        ref = SymbolReference(name="os")
        visitor.visit_symbol_reference(ref)
        assert output.getvalue() == "import os\n"

    def test_visit_symbol_reference_with_alias(self):
        output = StringIO()
        visitor = CodeGeneratorVisitor(output)
        ref = SymbolReference(name="os", alias="operating_system")
        visitor.visit_symbol_reference(ref)
        assert output.getvalue() == "import os as operating_system\n"

    def test_visit_function_symbol(self):
        output = StringIO()
        visitor = CodeGeneratorVisitor(output)
        func = FunctionSymbol(name="test_func", body="return 42")
        visitor.visit_function_symbol(func)
        expected = "def test_func():\n    return 42\n"
        assert output.getvalue() == expected

    def test_visit_class_symbol(self):
        output = StringIO()
        visitor = CodeGeneratorVisitor(output)
        cls = ClassSymbol(name="TestClass", body="pass")
        visitor.visit_class_symbol(cls)
        expected = "class TestClass:\n    pass\n"
        assert output.getvalue() == expected

    def test_visit_variable_symbol(self):
        output = StringIO()
        visitor = CodeGeneratorVisitor(output)
        var = VariableSymbol(name="x", body="42")
        visitor.visit_variable_symbol(var)
        assert output.getvalue() == "x = 42\n"
