from dill import dumps, loads
from dill.source import getsource, importable, isdynamic


def test_lambda():
    fn = lambda x, y: x + y  # noqa : E731

    assert getsource(fn, lstrip=True) == "fn = lambda x, y: x + y  # noqa : E731\n"


def root(a: int):
    def inner(b: int):
        return a + b

    return inner


def test_inner_function():
    # test used to discover dill capabilities
    fn = root(a=1)
    assert fn(b=1) == 2
    assert loads(dumps(fn))(1) == 2

    print(_encode(fn))

    print(_encode(lambda x, y: x + y, "mine"))

    assert not isdynamic(fn)
    assert importable(fn) == "from tests import inner\n"


def _encode(fn, name: str | None = None) -> str:
    prelude = "# " + "\n# ".join(getsource(fn).split("\n")) + "\n\n"
    code = f"""
    def {name if name else "factory"}():
        from dill import loads
        return loads({dumps(fn, recurse=True)})
    """
    return prelude + code


def save_state():
    import io

    import dill

    buf = io.BytesIO()
    dill.dump_module(buf, refimported=True)


def load_state():
    import dill

    dill.load_module()
