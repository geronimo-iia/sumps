import builtins

from sumps.lang.module_builder import GlobalEnvironmentBuilder
from sumps.lang.symbols import LocalSymbol, SymbolReference


class TestGlobalEnvironmentBuilder:
    def test_init_minimal_globals(self):
        builder = GlobalEnvironmentBuilder()
        assert builder._globals == {"__builtins__": builtins}
        assert builder._loaded_modules == {}

    def test_init_with_current_context(self):
        builder = GlobalEnvironmentBuilder(use_current_context=True)
        assert "__builtins__" in builder._globals
        assert len(builder._globals) > 1

    def test_build_returns_globals(self):
        builder = GlobalEnvironmentBuilder()
        result = builder.build()
        assert result == {"__builtins__": builtins}

    def test_visit_symbol_reference_basic(self):
        builder = GlobalEnvironmentBuilder()
        # Test that the method exists and can be called without error
        ref = SymbolReference(name="__test__")
        builder.visit_symbol_reference(ref)
        # Should be ignored due to private module name
        assert "__test__" not in builder._globals

    def test_visit_local_symbol(self):
        builder = GlobalEnvironmentBuilder()
        local_sym = LocalSymbol(name="test_var", reference="test_value")
        builder.visit_local_symbol(local_sym)

        assert builder._globals["test_var"] == "test_value"

    def test_ignore_private_modules(self):
        builder = GlobalEnvironmentBuilder()
        ref = SymbolReference(name="__private__")
        builder.visit_symbol_reference(ref)

        assert "__private__" not in builder._globals
