import pytest

from sumps.lang.symbols import Empty, SymbolReference, SymbolTable


class TestSymbolReference:
    def test_init_and_alias_property(self):
        ref = SymbolReference(name="module.submodule")
        assert ref.name == "submodule"
        assert ref.scope == "module"
        assert ref.kind == "import"
        assert ref.alias is None
        assert ref.annotation is Empty

        ref2 = SymbolReference(name="module.submodule", alias="mod", annotation="annot")
        assert ref2.alias == "mod"
        assert ref2.annotation == "annot"

    def test_str_without_alias(self):
        ref = SymbolReference(name="os.path")
        s = str(ref)
        assert s == "import os.path"

    def test_str_with_alias(self):
        ref = SymbolReference(name="os.path", alias="pathlib")
        s = str(ref)
        assert s == "import os.path as pathlib"


class TestSymbolTable:
    def test_init_defaults(self):
        table = SymbolTable()
        assert len(table) == 0

    def test_init_with_references(self):
        ref1 = SymbolReference(name="a")
        ref2 = SymbolReference(name="b", alias="bb")
        table = SymbolTable()
        table.add(ref1)
        table.add(ref2)
        assert table.all() == [ref1, ref2]

    def test_add_valid_and_invalid(self):
        table = SymbolTable()
        ref = table.add(SymbolReference(name="mod"))
        assert ref in table

        class FakeSymbol:
            kind = "function"
            name = "fake"

        fake = FakeSymbol()
        with pytest.raises(ValueError, match="Expected an import, got a function"):
            table.add(fake)  # type: ignore

    def test_add_reference_creates_and_adds(self):
        table = SymbolTable()
        ref = table.add_reference("sys", alias="system")
        assert isinstance(ref, SymbolReference)
        assert ref.name == "sys"
        assert ref.alias == "system"
        assert ref in table
