from io import StringIO

from sumps.lang.module_builder import DynamicModule, ModuleBuilder
from sumps.lang.symbols import FunctionSymbol, VariableSymbol


class TestModuleBuilder:
    def test_init_with_name(self):
        builder = ModuleBuilder(name="test_module")
        assert builder.name == "test_module"
        assert builder._locals is not None

    def test_init_without_name(self):
        builder = ModuleBuilder()
        assert builder.name.startswith("dynamic_")

    def test_add_statement_function(self):
        builder = ModuleBuilder(name="test_module")
        func = FunctionSymbol(name="test_func", body="return 42")
        result = builder.add_statement(func)

        assert result is builder
        assert len(builder.statements) == 1

    def test_add_statement_variable(self):
        builder = ModuleBuilder(name="test_module")
        var = VariableSymbol(name="x", body="42")
        builder.add_statement(var)

        assert len(builder.statements) == 1

    def test_encodes_generates_code(self):
        builder = ModuleBuilder(name="test_module")
        func = FunctionSymbol(name="test_func", body="return 42")
        builder.add_statement(func)

        output = StringIO()
        builder.encodes(output)
        code = output.getvalue()

        assert "def test_func():" in code
        assert "return 42" in code

    def test_build_returns_dynamic_module(self):
        builder = ModuleBuilder(name="test_module")
        func = FunctionSymbol(name="test_func", body="return 42")
        builder.add_statement(func)

        result = builder.build()

        assert isinstance(result, DynamicModule)
        assert result.name == builder.qualified_name

    def test_build_with_store_in_sys_modules(self):
        builder = ModuleBuilder(name="test_module")
        func = FunctionSymbol(name="test_func", body="return 42")
        builder.add_statement(func)

        result = builder.build(store_in_sys_modules=True)

        assert isinstance(result, DynamicModule)
