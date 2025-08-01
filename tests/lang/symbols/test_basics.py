from sumps.lang.symbols import ClassSymbol, FunctionSymbol, ModuleSymbol, ParameterSymbol, VariableSymbol


class TestFunctionSymbol:
    def test_basic(self):
        func = FunctionSymbol(name="my_func", parameters=[], return_annotation="int")
        assert func.name == "my_func"
        assert func.return_annotation == "int"
        assert func.parameters.all() == []

    def test_with_parameters(self):
        params = [ParameterSymbol(name="x", annotation="int"), ParameterSymbol(name="y", annotation="float")]
        func = FunctionSymbol(name="compute", parameters=params, return_annotation="float")
        assert len(func.parameters) == 2
        assert func.parameters["x"].name == "x"
        assert func.parameters["y"].annotation == "float"

    def test_eq_and_repr(self):
        f1 = FunctionSymbol("f", parameters=[], return_annotation="None")
        f2 = FunctionSymbol("f", parameters=[], return_annotation="None")
        f3 = FunctionSymbol("f", parameters=[ParameterSymbol("x", "int")], return_annotation="None")
        assert f1 == f2
        assert f1 != f3
        assert "FunctionSymbol(name='f'" in repr(f1)


class TestParameterSymbol:
    def test_repr(self):
        param = ParameterSymbol(name="z", annotation="str")
        assert repr(param) == "ParameterSymbol(name='z', parameter_kind='POSITIONAL_OR_KEYWORD', default=<class 'sumps.lang.symbols.Empty'>, annotation='str', scope=None)" #noqa: E501

    def test_eq(self):
        p1 = ParameterSymbol("arg",annotation="str")
        p2 = ParameterSymbol("arg", annotation="str")
        p3 = ParameterSymbol("arg", annotation="int")
        assert p1 == p2
        assert p1 != p3


class TestVariableSymbol:
    def test_creation(self):
        var = VariableSymbol(name="counter", annotation="int", body=42)
        assert var.name == "counter"
        assert var.annotation == "int"
        assert var.body == 42

    def test_repr_and_eq(self):
        var1 = VariableSymbol("a", annotation="int", body=1)
        var2 = VariableSymbol("a", annotation="int", body=1)
        var3 = VariableSymbol("a", annotation="float", body=1.0)
        assert var1 == var2
        assert var1 != var3
        assert repr(var1) == "VariableSymbol(name='a', annotation='int', scope=None), body=1"


class TestModuleSymbol:
    def test_add_and_get_function(self):
        module = ModuleSymbol(name="math_utils")
        func = FunctionSymbol("add", parameters=[],return_annotation= "int")
        module.statements.add(func)
        assert module.statements.get_function("add") == func
        assert module.statements.get_function("missing") is None

    def test_add_and_get_class(self):
        module = ModuleSymbol(name="shapes")
        cls = ClassSymbol(name="Circle",body="pass")
        module.statements.add(cls)
        assert module.statements.get_class("Circle") == cls
        assert module.statements.get_class("Square") is None


class TestClassSymbol:
    def test_inheritance_structure(self):
        derived = ClassSymbol(name="Dog", bases=["Animal"], body="pass")
        assert derived.name == "Dog"
        assert derived.bases == ["Animal"]
