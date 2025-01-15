from sumps.lang.symbols import Encoder, FunctionStatement, Module


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
