import builtins

import pytest

from sumps.lang.module_builder import GlobalEnvironmentBuilder
from sumps.lang.symbols import LocalSymbol, SymbolReference


@pytest.fixture
def builder():
    return GlobalEnvironmentBuilder()


@pytest.fixture
def builder_with_context():
    return GlobalEnvironmentBuilder(use_current_context=True)


def test_init_minimal_globals(builder):
    assert builder._globals == {"__builtins__": builtins}
    assert builder._loaded_modules == {}


def test_init_with_current_context(builder_with_context):
    assert "__builtins__" in builder_with_context._globals
    assert len(builder_with_context._globals) > 1


def test_build_returns_globals(builder):
    result = builder.build()
    assert result == {"__builtins__": builtins}


def test_visit_symbol_reference_os(builder):
    ref = SymbolReference(name="os")
    builder.visit_symbol_reference(ref)

    assert "os" in builder._globals
    assert "os" in builder._loaded_modules


def test_visit_local_symbol(builder):
    local_sym = LocalSymbol(name="test_var", reference="test_value")
    builder.visit_local_symbol(local_sym)

    assert builder._globals["test_var"] == "test_value"


def test_ignore_private_modules(builder):
    ref = SymbolReference(name="__private__")
    builder.visit_symbol_reference(ref)

    assert "__private__" not in builder._globals
