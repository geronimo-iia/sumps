from inspect import Parameter

import pytest

from sumps.lang.symbols.base import Empty
from sumps.lang.symbols.parameter import ParameterSymbol, Parameters, _parameter_kind_to_literal, _parameter_literal_to_kind


class TestParameterSymbol:
    def test_init_defaults(self):
        param = ParameterSymbol(name="x")
        assert param.name == "x"
        assert param.parameter_kind == "POSITIONAL_OR_KEYWORD"
        assert param.default is Empty
        assert param.annotation is Empty
        assert param.kind == "parameter"

    def test_init_full(self):
        param = ParameterSymbol(
            name="y",
            parameter_kind="VAR_POSITIONAL",
            annotation=int,
            default=42,
        )
        assert param.name == "y"
        assert param.parameter_kind == "VAR_POSITIONAL"
        assert param.annotation is int
        assert param.default == Empty
        assert param.kind == "parameter"

    def test_repr(self):
        param = ParameterSymbol(name="my_scope.z", parameter_kind="KEYWORD_ONLY", annotation=str, default="abc")
        repr_str = repr(param)
        assert "ParameterSymbol" in repr_str
        assert "name='z'" in repr_str
        assert "parameter_kind='KEYWORD_ONLY'" in repr_str
        assert "default='abc'" in repr_str
        assert "annotation=<class 'str'>" in repr_str
        assert "scope='my_scope'" in repr_str

    def test_to_inspect_parameter_without_defaults(self):
        param = ParameterSymbol(name="a", annotation=int)
        iparam = param.to_inspect_parameter()
        assert isinstance(iparam, Parameter)
        assert iparam.name == "a"
        assert iparam.kind == Parameter.POSITIONAL_OR_KEYWORD
        assert iparam.default is Parameter.empty
        assert iparam.annotation is int

    def test_to_inspect_parameter_positional_with_defaults(self):
        param = ParameterSymbol(name="b", parameter_kind="VAR_POSITIONAL", default=99, annotation=str)
        iparam = param.to_inspect_parameter()
        assert iparam.name == "b"
        assert iparam.kind == Parameter.VAR_POSITIONAL
        assert iparam.default is Parameter.empty
        assert iparam.annotation is str

    def test_to_inspect_parameter_keyword_with_defaults(self):
        param = ParameterSymbol(name="b", parameter_kind="VAR_KEYWORD", default=99, annotation=str)
        iparam = param.to_inspect_parameter()
        assert iparam.name == "b"
        assert iparam.kind == Parameter.VAR_KEYWORD
        assert iparam.default is Parameter.empty
        assert iparam.annotation is str

    def test_from_inspect_parameter_roundtrip(self):
        iparam = Parameter("c", Parameter.KEYWORD_ONLY, default=100, annotation=float)
        param_symbol = ParameterSymbol.from_inspect_parameter(iparam)
        assert param_symbol.name == "c"
        assert param_symbol.parameter_kind == "KEYWORD_ONLY"
        assert param_symbol.default == 100
        assert param_symbol.annotation is float

        iparam2 = param_symbol.to_inspect_parameter()
        assert iparam2.name == iparam.name
        assert iparam2.kind == iparam.kind
        assert iparam2.default == iparam.default
        assert iparam2.annotation == iparam.annotation

    def test_from_inspect_parameter_empty_defaults_and_annotations(self):
        iparam = Parameter("d", Parameter.POSITIONAL_ONLY)
        param_symbol = ParameterSymbol.from_inspect_parameter(iparam)
        assert param_symbol.default is Empty
        assert param_symbol.annotation is Empty


class TestParameterKindConversion:
    @pytest.mark.parametrize(
        "literal, expected_kind",
        [
            ("POSITIONAL_ONLY", Parameter.POSITIONAL_ONLY),
            ("POSITIONAL_OR_KEYWORD", Parameter.POSITIONAL_OR_KEYWORD),
            ("VAR_POSITIONAL", Parameter.VAR_POSITIONAL),
            ("KEYWORD_ONLY", Parameter.KEYWORD_ONLY),
            ("VAR_KEYWORD", Parameter.VAR_KEYWORD),
        ],
    )
    def test_literal_to_kind_valid(self, literal, expected_kind):
        kind = _parameter_literal_to_kind(literal)
        assert kind == expected_kind

    def test_literal_to_kind_invalid(self):
        with pytest.raises(ValueError):
            _parameter_literal_to_kind("INVALID_KIND")

    @pytest.mark.parametrize(
        "kind, expected_literal",
        [
            (Parameter.POSITIONAL_ONLY, "POSITIONAL_ONLY"),
            (Parameter.POSITIONAL_OR_KEYWORD, "POSITIONAL_OR_KEYWORD"),
            (Parameter.VAR_POSITIONAL, "VAR_POSITIONAL"),
            (Parameter.KEYWORD_ONLY, "KEYWORD_ONLY"),
            (Parameter.VAR_KEYWORD, "VAR_KEYWORD"),
        ],
    )
    def test_kind_to_literal_valid(self, kind, expected_literal):
        literal = _parameter_kind_to_literal(kind)
        assert literal == expected_literal

    def test_kind_to_literal_invalid(self):
        class FakeKind:
            pass

        with pytest.raises(ValueError):
            _parameter_kind_to_literal(FakeKind())


class TestParameters:
    def test_init_empty(self):
        params = Parameters()
        assert len(params) == 0
        assert list(params) == []

    def test_init_with_symbols(self):
        params = Parameters()
        params.add(ParameterSymbol(name="a"))
        params.add(ParameterSymbol(name="b"))
        assert len(params) == 2
        assert params["a"].name == "a"
        assert params["b"].name == "b"

    def test_add_accepts_only_parameter_symbol(self):
        params = Parameters()
        p = ParameterSymbol("param1")
        params.add(p)

        class DummySymbol:
            kind = "not-a-parameter"
            name = "dummy"
            qualified_name = "dummy"

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
        params.add(ParameterSymbol(name="x"))
        params.add(ParameterSymbol(name="y"))

        assert len(params) == 2
        names = [p.name for p in params]
        assert names == ["x", "y"]
        assert params["x"].name == "x"
        assert params["y"].name == "y"
        assert ("x" in params) is True
        assert ("z" in params) is False

    def test_remove_get_has_all_clear(self):
        params = Parameters()
        p1 = ParameterSymbol("a")
        p2 = ParameterSymbol("b")
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