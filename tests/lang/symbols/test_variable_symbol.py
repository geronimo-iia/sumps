from sumps.lang.symbols import Empty, VariableSymbol


class TestVariableSymbol:
    def test_init_defaults(self):
        var = VariableSymbol(name="x")
        assert var.name == "x"
        assert var.kind == "variable"
        assert var.annotation is Empty
        assert var.body == ""

    def test_init_with_annotation_and_body(self):
        var = VariableSymbol(name="y", annotation=int, body="42")
        assert var.name == "y"
        assert var.annotation is int
        assert var.body == "42"

    def test_str_with_annotation(self):
        var = VariableSymbol(name="z", annotation=str, body="'hello'")
        s = str(var)
        assert s == "z: <class 'str'> = 'hello'"

    def test_str_without_annotation(self):
        var = VariableSymbol(name="a", body="10")
        s = str(var)
        assert s == "a: Any = 10"

    def test_repr_contains_expected(self):
        var = VariableSymbol(name="var1", annotation=float, body="3.14")
        r = repr(var)
        assert r.startswith("VariableSymbol(")
        assert "name='var1'" in r
        assert "annotation=<class 'float'>" in r
        assert "body='3.14'" in r
