from sumps.lang import get_builtin_type_names, qualified_name


def test_get_builtin_type_names():
    assert get_builtin_type_names()
    assert "str" in get_builtin_type_names()


class Test:
    pass


def test_qualified_name():
    assert qualified_name("aa") == "str"
    assert qualified_name(Test()) == "tests.lang.test_types.Test"
