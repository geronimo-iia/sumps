from sumps.lang.symbols import Empty, ModuleSymbol, Statement, Statements, SymbolReference, SymbolTable


class DummyStatement(Statement):
    def __init__(self, name="dummy"):
        super().__init__(name=name, kind="dummy", body="", annotation=Empty)


class TestModuleSymbol:
    def test_init_defaults(self):
        mod = ModuleSymbol(name="mymodule")
        assert mod.name == "mymodule"
        assert mod.kind == "module"
        assert mod.docstring is None
        assert isinstance(mod.references, SymbolTable)
        assert isinstance(mod.statements, Statements)
        assert len(mod.statements) == 0
        assert len(mod.references) == 0
        assert mod.annotation is Empty

    def test_init_with_docstring_and_annotation(self):
        mod = ModuleSymbol(name="mod", docstring="Docstring", annotation="annot")
        assert mod.docstring == "Docstring"
        assert mod.annotation == "annot"

    def test_add_reference(self):
        mod = ModuleSymbol(name="mod")
        ref = mod.references.add_reference("os", alias="osmod")
        assert isinstance(ref, SymbolReference)
        assert ref.name == "os"
        assert ref.alias == "osmod"
        assert ref in mod.references

    def test_str_and_repr(self):
        mod = ModuleSymbol(name="mod")
        s = str(mod)
        assert s == f"module {mod.qualified_name}"

        r = repr(mod)
        assert r.startswith("ModuleSymbol(")
        assert "name='mod'" in r
        assert "statements=0" in r
