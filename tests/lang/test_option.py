from pytest import raises

from sumps.lang.option import Nothing, Option, Some, maybe
from tests.conftest import parametrize


def _raise(*args):
    raise ValueError


class MyOption(Option):
    def __new__(cls):
        super().__new__(cls, is_some=True, value=1)


def test_option_cannot_be_instanciated():
    with raises(RuntimeError):
        Option(is_some=True, value=1)

    with raises(RuntimeError):
        MyOption()


@parametrize(
    "obj,is_some",
    [
        (maybe(0), True),
        (maybe(0.0), True),
        (maybe(""), True),
        (maybe([]), True),
        (maybe({}), True),
        (maybe(()), True),
        (maybe(set()), True),
        (maybe(None), False),
        (maybe(1), True),
        (maybe(True), True),
        (maybe(False), True),
    ],
)
def test_maybe(obj, is_some):
    if is_some:
        assert obj.is_some
    else:
        assert obj.is_none


@parametrize("is_some", [True, False])
def test_no_option_init(is_some):
    with raises(RuntimeError):
        if is_some:
            Option(True, 1)
        else:
            Option(False, None)


@parametrize("obj,expected", [(Some(1), 1), (Some("test"), "test"), (Some(True), True)])
def test_some(obj, expected):
    assert obj.is_some is True
    assert obj.is_none is False
    assert bool(obj)
    assert obj.value == expected
    assert obj.unwrap() == expected
    assert obj.unwrap_or(default="other") == expected
    assert obj.expect(msg="bouh") == expected
    assert obj._value == expected


def test_some_cant_be_null():
    with raises(RuntimeError):
        Some(Nothing())
    with raises(RuntimeError):
        Some(None)


@parametrize("obj,expected", [(Some(1), True), (Nothing(), False)])
def test_bool(obj, expected):
    assert bool(obj) is expected


@parametrize("obj", [Nothing(), maybe(None)])
def test_none(obj):
    assert obj.is_some is False
    assert obj.is_none is True
    assert bool(obj) is False
    assert obj._value is None

    with raises(ValueError):
        obj.value  # noqa: B018

    with raises(ValueError):
        obj.unwrap()

    assert obj.unwrap_or(default="other") == "other"

    with raises(ValueError):
        obj.expect(msg="bouh")


def test_equality():
    assert Some(1) != Nothing()
    assert Some(1) != Nothing()
    assert Some(1) != Some(2)
    assert Some(1) == Some(1)


def test_partial_ordering():
    assert Some(1) >= Nothing()
    assert Nothing() <= Some(1)
    assert Some(1) > Nothing()
    assert Nothing() < Some(1)

    assert Nothing() <= Nothing()
    assert Nothing() >= Nothing()
    assert not (Nothing() < Nothing())
    assert not (Nothing() > Nothing())

    assert Some(1) < Some(2)
    assert Some(1) <= Some(2)
    assert Some(2) > Some(1)
    assert Some(2) >= Some(1)
    assert Some(1) >= Some(1)
    assert not (Some(1) > Some(1))


def test_zip():
    assert Some(1).zip(Some(2)) == Some((1, 2))
    assert Some(1).zip(Some(2)).unzip() == (Some(1), Some(2))

    assert Some(1).zip(Some(2)).zip(Some(3)) == Some(((1, 2), 3))
    assert Some(((1, 2), 3)).unzip() == (Some((1, 2)), Some(3))

    assert Some((1, 2, 3)).unzip() == (Some(1), Some((2, 3)))


def test_flatten():
    assert Some(Some(1)).flatten() == Some(1)


@parametrize(
    "obj,func,expected",
    [(Some(1), lambda x: x * 2, Some(2)), (Nothing(), _raise, Nothing()), (Some("asd"), len, Some(3))],
)
def test_map(obj, func, expected):
    assert obj.map(func) == expected


def test_and_then_flatmap_bind_equivalence():
    def f(x):
        return Some(x * 10)

    some = Some(2)
    nothing = Nothing()

    assert some.and_then(f) == Some(20)
    assert some.flatmap(f) == Some(20)
    assert some.bind(f) == Some(20)

    assert nothing.and_then(f) == Nothing()
    assert nothing.flatmap(f) == Nothing()
    assert nothing.bind(f) == Nothing()


def test_or_else_and_or():
    some = Some(5)
    nothing = Nothing()

    assert some | Some(10) == some
    assert nothing | Some(10) == Some(10)
    assert nothing | Nothing() == Nothing()

    or_else_result = nothing.or_else(lambda: 42)
    assert or_else_result == Some(42)

    or_else_result_some = some.or_else(lambda: 42)
    assert or_else_result_some == some


def test_and_operator():
    some1 = Some(1)
    some2 = Some(2)
    nothing = Nothing()

    assert (some1 & some2) == some2
    assert (some1 & nothing) == Nothing()
    assert (nothing & some2) == Nothing()
    assert (nothing & nothing) == Nothing()


def test_xor_operator():
    some1 = Some(1)
    some2 = Some(2)
    nothing = Nothing()

    assert (some1 ^ some2) == Nothing()
    assert (some1 ^ nothing) == some1
    assert (nothing ^ some2) == some2
    assert (nothing ^ nothing) == Nothing()


def test_map_or_and_map_or_else():
    some = Some(3)
    nothing = Nothing()

    assert some.map_or(lambda x: x * 2, 10) == 6
    assert nothing.map_or(lambda x: x * 2, 10) == 10

    assert some.map_or_else(lambda x: x * 3, lambda: 7) == 9
    assert nothing.map_or_else(lambda x: x * 3, lambda: 7) == 7


def test_filter_behavior():
    some = Some(10)
    nothing = Nothing()

    assert some.filter(lambda x: x > 5) == some
    assert some.filter(lambda x: x < 5) == Nothing()
    assert nothing.filter(lambda x: True) == Nothing()


def test_get_method_with_mapping():
    some_map = Some({"a": 1, "b": 2})
    nothing = Nothing()

    assert some_map.get("a") == Some(1)
    assert some_map.get("c") == Nothing()
    assert some_map.get("c", default=5) == Some(5)
    assert nothing.get("a") == Nothing()
    assert nothing.get("a", default=5) == Some(5)


def test_hash_and_repr_consistency():
    s1 = Some(1)
    s2 = Some(1)
    n1 = Nothing()
    n2 = Nothing()

    assert hash(s1) == hash(s2)
    assert hash(n1) == hash(n2)
    assert repr(s1) == "Some(1)"
    assert repr(n1) == "Nothing"


def test_expect_message():
    nothing = Nothing()
    with raises(ValueError, match="custom error"):
        nothing.expect("custom error")


def test_unwrap_or_else():
    some = Some(5)
    nothing = Nothing()

    assert some.unwrap_or_else(lambda: 10) == 5
    assert nothing.unwrap_or_else(lambda: 10) == 10
