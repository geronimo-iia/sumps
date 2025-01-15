"""Unit test for stringcase"""


def assert_equal(a, b):
    assert a == b


def test_camel_case():
    from sumps.lang.stringcase import camel_case

    assert_equal("fooBar", camel_case("foo_bar"))
    assert_equal("fooBar", camel_case("FooBar"))
    assert_equal("fooBar", camel_case("foo-bar"))
    assert_equal("fooBar", camel_case("foo.bar"))
    assert_equal("barBaz", camel_case("_bar_baz"))
    assert_equal("barBaz", camel_case(".bar_baz"))
    assert_equal("", camel_case(""))
    assert_equal("none", camel_case(None))
    assert_equal("fooBarBaz", camel_case("Foo Bar Baz"))
    assert_equal("me", camel_case("_me"))
    assert_equal("me", camel_case("__me"))
    assert_equal("me", camel_case("-_me"))


def test_capital_case():
    from sumps.lang.stringcase import capital_case

    assert_equal("", capital_case(""))
    assert_equal("FooBar", capital_case("fooBar"))
    assert_equal("None", capital_case(None))


def test_const_case():
    from sumps.lang.stringcase import const_case

    assert_equal("FOO_BAR", const_case("fooBar"))
    assert_equal("FOO_BAR", const_case("foo_bar"))
    assert_equal("FOO_BAR", const_case("foo-bar"))
    assert_equal("FOO_BAR", const_case("foo.bar"))
    assert_equal("_BAR_BAZ", const_case("_bar_baz"))
    assert_equal("_BAR_BAZ", const_case(".bar_baz"))
    assert_equal("", const_case(""))
    assert_equal("NONE", const_case(None))


def test_lower_case():
    from sumps.lang.stringcase import lower_case

    assert_equal("none", lower_case(None))
    assert_equal("", lower_case(""))
    assert_equal("foo", lower_case("Foo"))


def test_pascal_case():
    from sumps.lang.stringcase import pascal_case

    assert_equal("FooBar", pascal_case("foo_bar"))
    assert_equal("FooBar", pascal_case("foo-bar"))
    assert_equal("FooBar", pascal_case("foo.bar"))
    assert_equal("BarBaz", pascal_case("_bar_baz"))
    assert_equal("BarBaz", pascal_case(".bar_baz"))
    assert_equal("", pascal_case(""))
    assert_equal("None", pascal_case(None))


def test_path_case():
    from sumps.lang.stringcase import path_case

    assert_equal("foo/bar", path_case("fooBar"))
    assert_equal("foo/bar", path_case("foo_bar"))
    assert_equal("foo/bar", path_case("foo-bar"))
    assert_equal("foo/bar", path_case("foo.bar"))
    assert_equal("/bar/baz", path_case("_bar_baz"))
    assert_equal("/bar/baz", path_case(".bar_baz"))
    assert_equal("", path_case(""))
    assert_equal("none", path_case(None))


def test_sentence_case():
    from sumps.lang.stringcase import sentence_case

    assert_equal("Foo bar", sentence_case("fooBar"))
    assert_equal("Foo bar", sentence_case("foo_bar"))
    assert_equal("Foo bar", sentence_case("foo-bar"))
    assert_equal("Foo bar", sentence_case("foo.bar"))
    assert_equal("Bar baz", sentence_case("_bar_baz"))
    assert_equal("Bar baz", sentence_case(".bar_baz"))
    assert_equal("", sentence_case(""))
    assert_equal("None", sentence_case(None))


def test_upper_case():
    from sumps.lang.stringcase import upper_case

    assert_equal("NONE", upper_case(None))
    assert_equal("", upper_case(""))
    assert_equal("FOO", upper_case("foo"))


def test_snake_case():
    from sumps.lang.stringcase import snake_case

    assert_equal("foo_bar", snake_case("fooBar"))
    assert_equal("foo_bar", snake_case("foo_bar"))
    assert_equal("foo_bar", snake_case("foo-bar"))
    assert_equal("foo_bar", snake_case("foo.bar"))
    assert_equal("_bar_baz", snake_case("_bar_baz"))
    assert_equal("_bar_baz", snake_case(".bar_baz"))
    assert_equal("", snake_case(""))
    assert_equal("none", snake_case(None))


def test_spinal_case():
    from sumps.lang.stringcase import spinal_case

    assert_equal("foo-bar", spinal_case("fooBar"))
    assert_equal("foo-bar", spinal_case("foo_bar"))
    assert_equal("foo-bar", spinal_case("foo-bar"))
    assert_equal("foo-bar", spinal_case("foo.bar"))
    assert_equal("-bar-baz", spinal_case("_bar_baz"))
    assert_equal("-bar-baz", spinal_case(".bar_baz"))
    assert_equal("", spinal_case(""))
    assert_equal("none", spinal_case(None))


def test_dot_case():
    from sumps.lang.stringcase import dot_case

    assert_equal("foo.bar", dot_case("fooBar"))
    assert_equal("foo.bar", dot_case("foo_bar"))
    assert_equal("foo.bar", dot_case("foo-bar"))
    assert_equal("foo.bar", dot_case("foo.bar"))
    assert_equal(".bar.baz", dot_case("_bar_baz"))
    assert_equal(".bar.baz", dot_case(".bar_baz"))
    assert_equal("", dot_case(""))
    assert_equal("none", dot_case(None))


def test_title_case():
    from sumps.lang.stringcase import title_case

    assert_equal("Foo Bar", title_case("fooBar"))
    assert_equal("Foo Bar", title_case("foo_bar"))
    assert_equal("Foo Bar", title_case("foo-bar"))
    assert_equal("Foo Bar", title_case("foo.bar"))
    assert_equal(" Bar Baz", title_case("_bar_baz"))
    assert_equal(" Bar Baz", title_case(".bar_baz"))
    assert_equal("", title_case(""))
    assert_equal("None", title_case(None))


def test_trim_case():
    from sumps.lang.stringcase import trim_case

    assert_equal("foo bar baz", trim_case(" foo bar baz "))
    assert_equal("", trim_case(""))
    assert_equal("None", trim_case(None))


def test_alphanum_case():
    from sumps.lang.stringcase import alphanum_case

    assert_equal("FooBar", alphanum_case("_Foo., Bar"))
    assert_equal("Foo123Bar", alphanum_case("Foo_123 Bar!"))
    assert_equal("", alphanum_case(""))
    assert_equal("None", alphanum_case(None))
