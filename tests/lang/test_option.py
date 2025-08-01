from pytest import raises

from sumps.lang.option import Nothing, Option, Some, maybe


class TestOption:
    def test_cannot_be_instantiated(self):
        with raises(RuntimeError):
            Option(is_some=True, value=1)

        class MyOption(Option):
            def __new__(cls):
                super().__new__(cls, is_some=True, value=1)

        with raises(RuntimeError):
            MyOption()

    def test_no_option_init(self):
        with raises(RuntimeError):
            Option(True, 1)
        with raises(RuntimeError):
            Option(False, None)


class TestMaybe:
    def test_maybe_values(self):
        assert maybe(0).is_some
        assert maybe(0.0).is_some
        assert maybe("").is_some
        assert maybe([]).is_some
        assert maybe({}).is_some
        assert maybe(()).is_some
        assert maybe(set()).is_some
        assert maybe(None).is_none
        assert maybe(1).is_some
        assert maybe(True).is_some
        assert maybe(False).is_some


class TestSome:
    def test_some_properties(self):
        obj = Some(1)
        assert obj.is_some is True
        assert obj.is_none is False
        assert bool(obj)
        assert obj.value == 1
        assert obj.unwrap() == 1
        assert obj.unwrap_or(default="other") == 1
        assert obj.expect(msg="bouh") == 1
        assert obj._value == 1

    def test_some_cant_be_null(self):
        with raises(RuntimeError):
            Some(Nothing())
        with raises(RuntimeError):
            Some(None)

    def test_bool_conversion(self):
        assert bool(Some(1)) is True
        assert bool(Nothing()) is False


class TestNothing:
    def test_nothing_properties(self):
        for obj in [Nothing(), maybe(None)]:
            assert obj.is_some is False
            assert obj.is_none is True
            assert bool(obj) is False
            assert obj._value is None

            with raises(ValueError):
                obj.value

            with raises(ValueError):
                obj.unwrap()

            assert obj.unwrap_or(default="other") == "other"

            with raises(ValueError):
                obj.expect(msg="bouh")


class TestOptionOperations:
    def test_equality(self):
        assert Some(1) != Nothing()
        assert Some(1) != Some(2)
        assert Some(1) == Some(1)

    def test_partial_ordering(self):
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

    def test_zip(self):
        assert Some(1).zip(Some(2)) == Some((1, 2))
        assert Some(1).zip(Some(2)).unzip() == (Some(1), Some(2))
        assert Some(1).zip(Some(2)).zip(Some(3)) == Some(((1, 2), 3))
        assert Some(((1, 2), 3)).unzip() == (Some((1, 2)), Some(3))
        assert Some((1, 2, 3)).unzip() == (Some(1), Some((2, 3)))

    def test_flatten(self):
        assert Some(Some(1)).flatten() == Some(1)

    def test_map(self):
        def _raise(*args):
            raise ValueError

        assert Some(1).map(lambda x: x * 2) == Some(2)
        assert Nothing().map(_raise) == Nothing()
        assert Some("asd").map(len) == Some(3)

    def test_and_then_flatmap_bind_equivalence(self):
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

    def test_or_else_and_or(self):
        some = Some(5)
        nothing = Nothing()

        assert some | Some(10) == some
        assert nothing | Some(10) == Some(10)
        assert nothing | Nothing() == Nothing()

        or_else_result = nothing.or_else(lambda: 42)
        assert or_else_result == Some(42)

        or_else_result_some = some.or_else(lambda: 42)
        assert or_else_result_some == some

    def test_and_operator(self):
        some1 = Some(1)
        some2 = Some(2)
        nothing = Nothing()

        assert (some1 & some2) == some2
        assert (some1 & nothing) == Nothing()
        assert (nothing & some2) == Nothing()
        assert (nothing & nothing) == Nothing()

    def test_xor_operator(self):
        some1 = Some(1)
        some2 = Some(2)
        nothing = Nothing()

        assert (some1 ^ some2) == Nothing()
        assert (some1 ^ nothing) == some1
        assert (nothing ^ some2) == some2
        assert (nothing ^ nothing) == Nothing()

    def test_map_or_and_map_or_else(self):
        some = Some(3)
        nothing = Nothing()

        assert some.map_or(lambda x: x * 2, 10) == 6
        assert nothing.map_or(lambda x: x * 2, 10) == 10

        assert some.map_or_else(lambda x: x * 3, lambda: 7) == 9
        assert nothing.map_or_else(lambda x: x * 3, lambda: 7) == 7

    def test_filter_behavior(self):
        some = Some(10)
        nothing = Nothing()

        assert some.filter(lambda x: x > 5) == some
        assert some.filter(lambda x: x < 5) == Nothing()
        assert nothing.filter(lambda x: True) == Nothing()

    def test_get_method_with_mapping(self):
        some_map = Some({"a": 1, "b": 2})
        nothing = Nothing()

        assert some_map.get("a") == Some(1)
        assert some_map.get("c") == Nothing()
        assert some_map.get("c", default=5) == Some(5)
        assert nothing.get("a") == Nothing()
        assert nothing.get("a", default=5) == Some(5)

    def test_hash_and_repr_consistency(self):
        s1 = Some(1)
        s2 = Some(1)
        n1 = Nothing()
        n2 = Nothing()

        assert hash(s1) == hash(s2)
        assert hash(n1) == hash(n2)
        assert repr(s1) == "Some(1)"
        assert repr(n1) == "Nothing"

    def test_expect_message(self):
        nothing = Nothing()
        with raises(ValueError, match="custom error"):
            nothing.expect("custom error")

    def test_unwrap_or_else(self):
        some = Some(5)
        nothing = Nothing()

        assert some.unwrap_or_else(lambda: 10) == 5
        assert nothing.unwrap_or_else(lambda: 10) == 10
