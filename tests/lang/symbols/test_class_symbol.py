from sumps.lang.symbols import ClassSymbol, Empty


class TestClassSymbol:
    def test_init_defaults(self):
        cls = ClassSymbol(name="MyClass", body="pass")
        assert cls.name == "MyClass"
        assert cls.kind == "class"
        assert cls.body == "pass"
        assert cls.bases == []
        assert cls.decorators == []
        assert cls.annotation is Empty

    def test_init_with_bases_and_decorators(self):
        bases = ["Base1", "Base2"]
        decorators = ["decorator1", "decorator2"]
        cls = ClassSymbol(name="ChildClass", bases=bases, decorators=decorators, body="pass")
        assert cls.bases == bases
        assert cls.decorators == decorators

    def test_add_base_and_decorator(self):
        cls = ClassSymbol(name="Test", body="pass")
        cls.add_base("Base")
        cls.add_decorator("staticmethod")
        assert "Base" in cls.bases
        assert "staticmethod" in cls.decorators

    def test_str_without_bases(self):
        cls = ClassSymbol(name="Simple", body="pass")
        s = str(cls)
        assert s == "class Simple"

    def test_str_with_bases(self):
        cls = ClassSymbol(name="Child", bases=["Base1", "Base2"], body="pass")
        s = str(cls)
        assert s == "class Child(Base1, Base2)"

    def test_repr_contains_expected_fields(self):
        cls = ClassSymbol(name="ReprTest", bases=["B"], decorators=["d"], body="pass")
        r = repr(cls)
        assert r.startswith("ClassSymbol(")
        assert "name='ReprTest'" in r
        assert "bases=['B']" in r
        assert "decorators=['d']" in r
        assert "body='pass'" in r
