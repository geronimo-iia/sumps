from inspect import Parameter, Signature

from sumps.lang.symbols.base import Empty
from sumps.lang.symbols.parameter import ParameterSymbol
from sumps.lang.symbols.statement import ClassSymbol, FunctionSymbol, Statement, Statements, VariableSymbol


def make_param(name="x", **kwargs):
    return ParameterSymbol(name=name, **kwargs)


class TestFunctionSymbol:
    def test_init_defaults(self):
        f = FunctionSymbol("foo")
        assert f.name == "foo"
        assert f.kind == "function"
        assert f.return_annotation == Empty
        assert f.is_async is False
        assert f.annotation == Empty
        assert f.body == ""

    def test_init_with_params_and_return(self):
        params = [make_param("a"), make_param("b")]
        f = FunctionSymbol("bar", parameters=params, return_annotation="int", body="pass", is_async=True)
        assert f.name == "bar"
        assert f.is_async is True
        assert f.return_annotation == "int"
        assert f.body == "pass"
        assert len(f.parameters) == 2
        assert f.parameters["a"].name == "a"
        assert f.annotation == "int"

    def test_str_method_and_signature(self):
        params = [make_param("a"), make_param("b")]
        f = FunctionSymbol("baz", parameters=params, return_annotation=str, is_async=True)
        sig = f.get_signature()
        assert isinstance(sig, Signature)
        assert len(sig.parameters) == 2
        s = str(f)
        assert s.startswith("async def baz")
        assert "(" in s and ")" in s

    def test_get_signature_returns_signature_with_correct_return_annotation(self):
        params = [make_param("x")]
        f = FunctionSymbol("qux", parameters=params, return_annotation=int)
        sig = f.get_signature()
        assert isinstance(sig, Signature)
        assert sig.return_annotation is int
        f_none = FunctionSymbol("no_return", parameters=params)
        sig_none = f_none.get_signature()
        assert sig_none.return_annotation == Signature.empty

    def test_from_signature_classmethod_creates_functionsymbol(self):
        params = [
            Parameter("x", Parameter.POSITIONAL_OR_KEYWORD),
            Parameter("y", Parameter.KEYWORD_ONLY, default=42),
        ]
        sig = Signature(params, return_annotation=int)
        f = FunctionSymbol.from_signature("func", sig, is_async=True, body="return x + y")
        assert isinstance(f, FunctionSymbol)
        assert f.name == "func"
        assert f.is_async is True
        assert f.body == "return x + y"
        assert f.return_annotation is int
        assert len(f.parameters) == 2
        assert all(isinstance(p, ParameterSymbol) for p in f.parameters)

    def test_add_parameter_delegates_to_parameters(self):
        f = FunctionSymbol("f")
        p = f.parameters.add_parameter("param1", parameter_kind="KEYWORD_ONLY", annotation=int, default=7)
        assert isinstance(p, ParameterSymbol)
        assert p.name == "param1"
        assert p.parameter_kind == "KEYWORD_ONLY"
        assert p.annotation is int
        assert p.default == 7
        assert f.parameters.has("param1")

    def test_iter_allows_iteration_over_parameters(self):
        params = [make_param("a"), make_param("b")]
        f = FunctionSymbol("foo", parameters=params)
        collected_names = [p.name for p in f]
        assert collected_names == ["a", "b"]

    def test_repr_contains_expected_info(self):
        params = [make_param("param")]
        f = FunctionSymbol("func", parameters=params, return_annotation="str")
        r = repr(f)
        assert "FunctionSymbol" in r
        assert "func" in r
        assert "param" in r
        assert "str" in r


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


class TestStatements:
    def test_get_variable(self):
        statements = Statements()
        var = VariableSymbol("test_var", body="42")
        statements.add(var)
        assert statements.get_variable("test_var") == var
        assert statements.get_variable("missing") is None

    def test_get_function(self):
        statements = Statements()
        func = FunctionSymbol("test_func")
        statements.add(func)
        assert statements.get_function("test_func") == func
        assert statements.get_function("missing") is None

    def test_get_class(self):
        statements = Statements()
        cls = ClassSymbol("TestClass", body="pass")
        statements.add(cls)
        assert statements.get_class("TestClass") == cls
        assert statements.get_class("Missing") is None


class TestStatement:
    def test_repr(self):
        class DummyStatement(Statement):
            def __init__(self):
                super().__init__(name="dummy", kind="dummy", body="pass", annotation=None)

        stmt = DummyStatement()
        repr_str = repr(stmt)
        assert "DummyStatement" in repr_str
        assert "dummy" in repr_str
        assert "pass" in repr_str