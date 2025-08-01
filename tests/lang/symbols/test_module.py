from sumps.lang.symbols.base import Empty
from sumps.lang.symbols.module import ModuleSymbol
from sumps.lang.symbols.reference import SymbolReference
from sumps.lang.symbols.statement import ClassSymbol, FunctionSymbol


class TestModuleSymbol:
    def test_init_defaults(self):
        mod = ModuleSymbol(name="mymodule")
        assert mod.name == "mymodule"
        assert mod.kind == "module"
        assert mod.docstring is None
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

    def test_add_and_get_function(self):
        module = ModuleSymbol(name="math_utils")
        func = FunctionSymbol("add", parameters=[], return_annotation="int")
        module.statements.add(func)
        assert module.statements.get_function("add") == func
        assert module.statements.get_function("missing") is None

    def test_add_and_get_class(self):
        module = ModuleSymbol(name="shapes")
        cls = ClassSymbol(name="Circle", body="pass")
        module.statements.add(cls)
        assert module.statements.get_class("Circle") == cls
        assert module.statements.get_class("Square") is None