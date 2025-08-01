from sumps.lang.symbols import Encoder, FunctionStatement, Module, get_builtin_type_names, get_type_qualified_name


def test_module():
    m = Module(name="test")
    output = Encoder.encoder()
    m.encode(output=output)
    assert output.getvalue()


def test_module_with_function():
    m = Module(name="test")
    f = FunctionStatement(name="add", annotation=int)
    f.add_parameter(name="a", annotation=int, default=0)
    f.add_parameter(name="b", annotation=int, default=0)
    f.body = "return a + b"
    m.statements.add(f)

    output = Encoder.encoder()
    m.encode(output=output)
    # print(output.getvalue())
    assert output.getvalue()


def test_get_builtin_type_names():
    assert get_builtin_type_names()
    assert "str" in get_builtin_type_names()


class Test:
    pass


def test_qualified_name():
    assert get_type_qualified_name("aa") == "str"
    assert get_type_qualified_name(Test()) == "tests.lang.test_symbols.Test"
