from sumps.lang.stringcase import (
    alphanum_case,
    camel_case,
    capital_case,
    const_case,
    dot_case,
    lower_case,
    pascal_case,
    path_case,
    sentence_case,
    snake_case,
    spinal_case,
    title_case,
    trim_case,
    upper_case,
)


class TestStringCase:
    def test_camel_case(self):
        assert camel_case("foo_bar") == "fooBar"
        assert camel_case("FooBar") == "fooBar"
        assert camel_case("foo-bar") == "fooBar"
        assert camel_case("foo.bar") == "fooBar"
        assert camel_case("_bar_baz") == "barBaz"
        assert camel_case(".bar_baz") == "barBaz"
        assert camel_case("") == ""
        assert camel_case(None) == "none"
        assert camel_case("Foo Bar Baz") == "fooBarBaz"
        assert camel_case("_me") == "me"
        assert camel_case("__me") == "me"
        assert camel_case("-_me") == "me"

    def test_capital_case(self):
        assert capital_case("") == ""
        assert capital_case("fooBar") == "FooBar"
        assert capital_case(None) == "None"

    def test_const_case(self):
        assert const_case("fooBar") == "FOO_BAR"
        assert const_case("foo_bar") == "FOO_BAR"
        assert const_case("foo-bar") == "FOO_BAR"
        assert const_case("foo.bar") == "FOO_BAR"
        assert const_case("_bar_baz") == "_BAR_BAZ"
        assert const_case(".bar_baz") == "_BAR_BAZ"
        assert const_case("") == ""
        assert const_case(None) == "NONE"

    def test_lower_case(self):
        assert lower_case(None) == "none"
        assert lower_case("") == ""
        assert lower_case("Foo") == "foo"

    def test_pascal_case(self):
        assert pascal_case("foo_bar") == "FooBar"
        assert pascal_case("foo-bar") == "FooBar"
        assert pascal_case("foo.bar") == "FooBar"
        assert pascal_case("_bar_baz") == "BarBaz"
        assert pascal_case(".bar_baz") == "BarBaz"
        assert pascal_case("") == ""
        assert pascal_case(None) == "None"

    def test_path_case(self):
        assert path_case("fooBar") == "foo/bar"
        assert path_case("foo_bar") == "foo/bar"
        assert path_case("foo-bar") == "foo/bar"
        assert path_case("foo.bar") == "foo/bar"
        assert path_case("_bar_baz") == "/bar/baz"
        assert path_case(".bar_baz") == "/bar/baz"
        assert path_case("") == ""
        assert path_case(None) == "none"

    def test_sentence_case(self):
        assert sentence_case("fooBar") == "Foo bar"
        assert sentence_case("foo_bar") == "Foo bar"
        assert sentence_case("foo-bar") == "Foo bar"
        assert sentence_case("foo.bar") == "Foo bar"
        assert sentence_case("_bar_baz") == "Bar baz"
        assert sentence_case(".bar_baz") == "Bar baz"
        assert sentence_case("") == ""
        assert sentence_case(None) == "None"

    def test_upper_case(self):
        assert upper_case(None) == "NONE"
        assert upper_case("") == ""
        assert upper_case("foo") == "FOO"

    def test_snake_case(self):
        assert snake_case("fooBar") == "foo_bar"
        assert snake_case("foo_bar") == "foo_bar"
        assert snake_case("foo-bar") == "foo_bar"
        assert snake_case("foo.bar") == "foo_bar"
        assert snake_case("_bar_baz") == "_bar_baz"
        assert snake_case(".bar_baz") == "_bar_baz"
        assert snake_case("") == ""
        assert snake_case(None) == "none"

    def test_spinal_case(self):
        assert spinal_case("fooBar") == "foo-bar"
        assert spinal_case("foo_bar") == "foo-bar"
        assert spinal_case("foo-bar") == "foo-bar"
        assert spinal_case("foo.bar") == "foo-bar"
        assert spinal_case("_bar_baz") == "-bar-baz"
        assert spinal_case(".bar_baz") == "-bar-baz"
        assert spinal_case("") == ""
        assert spinal_case(None) == "none"

    def test_dot_case(self):
        assert dot_case("fooBar") == "foo.bar"
        assert dot_case("foo_bar") == "foo.bar"
        assert dot_case("foo-bar") == "foo.bar"
        assert dot_case("foo.bar") == "foo.bar"
        assert dot_case("_bar_baz") == ".bar.baz"
        assert dot_case(".bar_baz") == ".bar.baz"
        assert dot_case("") == ""
        assert dot_case(None) == "none"

    def test_title_case(self):
        assert title_case("fooBar") == "Foo Bar"
        assert title_case("foo_bar") == "Foo Bar"
        assert title_case("foo-bar") == "Foo Bar"
        assert title_case("foo.bar") == "Foo Bar"
        assert title_case("_bar_baz") == " Bar Baz"
        assert title_case(".bar_baz") == " Bar Baz"
        assert title_case("") == ""
        assert title_case(None) == "None"

    def test_trim_case(self):
        assert trim_case(" foo bar baz ") == "foo bar baz"
        assert trim_case("") == ""
        assert trim_case(None) == "None"

    def test_alphanum_case(self):
        assert alphanum_case("_Foo., Bar") == "FooBar"
        assert alphanum_case("Foo_123 Bar!") == "Foo123Bar"
        assert alphanum_case("") == ""
        assert alphanum_case(None) == "None"
