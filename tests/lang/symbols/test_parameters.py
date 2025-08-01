import pytest

from sumps.lang.symbols import Empty, Parameters, ParameterSymbol


class DummySymbol:
    """Dummy class to test rejection in Parameters.add"""

    kind = "not-a-parameter"
    name = "dummy"


def make_param(name="p", **kwargs):
    return ParameterSymbol(name=name, **kwargs)


class TestParameters:
    def test_init_empty(self):
        params = Parameters()
        assert len(params) == 0
        assert list(params) == []

    def test_init_with_symbols(self):
        params = Parameters()
        params.add(make_param(name="a"))
        params.add(make_param(name="b"))
        assert len(params) == 2
        assert params["a"].name == "a"
        assert params["b"].name == "b"

    def test_add_accepts_only_parameter_symbol(self):
        params = Parameters()
        p = make_param("param1")
        params.add(p)

        dummy = DummySymbol()
        with pytest.raises(ValueError):
            params.add(dummy)

    def test_add_parameter_creates_and_adds(self):
        params = Parameters()
        p = params.add_parameter("foo", parameter_kind="VAR_POSITIONAL", annotation=int, default=42)
        assert isinstance(p, ParameterSymbol)
        assert p.name == "foo"
        assert p.parameter_kind == "VAR_POSITIONAL"
        assert p.annotation is int
        assert p.default == Empty
        assert params.has("foo")
        assert params.get("foo") == p

    def test_len_iter_getitem_contains(self):
        params = Parameters()
        params.add(make_param(name="x"))
        params.add(make_param(name="y"))

        assert len(params) == 2
        names = [p.name for p in params]
        assert names == ["x", "y"]
        assert params["x"].name == "x"
        assert params["y"].name == "y"
        assert ("x" in params) is True
        assert ("z" in params) is False

    def test_remove_get_has_all_clear(self):
        params = Parameters()
        p1 = make_param("a")
        p2 = make_param("b")
        params.add(p1)
        params.add(p2)

        assert params.has("a")
        assert params.has("b")

        params.remove("a")
        assert not params.has("a")
        assert params.has("b")

        all_syms = params.all()
        assert len(all_syms) == 1
        assert all_syms[0].name == "b"

        params.clear()
        assert len(params) == 0
        assert list(params) == []
