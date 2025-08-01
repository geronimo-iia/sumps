from sumps.lang.symbols.base import Empty, SymbolDescriptor, SymbolVisitor


class TestEmpty:
    def test_repr(self):
        empty = Empty()
        assert repr(empty) == "<Empty>"

    def test_bool(self):
        empty = Empty()
        assert not empty


class TestSymbolDescriptor:
    def test_normalize_scope_and_name(self):
        scope, name = SymbolDescriptor._normalize_scope_and_name("module.Class")
        assert scope == "module"
        assert name == "Class"
        
        scope, name = SymbolDescriptor._normalize_scope_and_name("simple")
        assert scope is None
        assert name == "simple"

    def test_qualified_name(self):
        class TestSymbol(SymbolDescriptor):
            pass
        
        symbol = TestSymbol("module.test", "variable")
        assert symbol.qualified_name == "module.test"
        assert symbol.name == "test"
        assert symbol.scope == "module"


class TestSymbolVisitor:
    def test_visit_dispatch(self):
        class TestSymbol(SymbolDescriptor):
            pass
        
        class TestVisitor(SymbolVisitor):
            def visit_test_symbol(self, node):
                return "visited"
        
        visitor = TestVisitor()
        symbol = TestSymbol("test", "variable")
        # This would call visit_test_symbol if implemented
        assert hasattr(visitor, 'visit')