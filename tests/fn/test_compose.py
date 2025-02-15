from inspect import signature

from sumps.func.compose import Compose, compose, pipe
from sumps.func.identity import identity


def add(a: int, b: int) -> int:
    return a + b


def double(a: int) -> int:
    return a * a


def test_compose_no_args():
    fn = compose()

    assert fn
    assert fn == identity
    assert fn(1) == 1
    assert fn("a") == "a"


def test_compose_single_args():
    fn = compose(add)
    assert fn
    assert fn == add


def test_compose():
    fn = compose(double, add)
    assert fn
    assert fn(1, 2) == 9


def test_pipe():
    fn = pipe(add, double)
    assert fn
    assert fn(1, 2) == 9


def test_signature():
    fn = compose(double, add)
    sig = str(signature(fn))
    assert sig == "(a: 'int', b: 'int') -> 'int'"


def test_compile():
    fn = Compose(funcs=[double, add]).compile()
    assert fn(1, 2) == 9
    fn = Compose(funcs=[double, double]).compile()
    assert fn(2) == 16
