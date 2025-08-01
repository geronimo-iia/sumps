from sumps.lang.named import Named, is_private, is_public, match_visibility


class TestNamed:
    def test_is_public(self):
        assert is_public(name="test")
        assert not is_public(name="_test")
        assert not is_public(name="__test")

    def test_is_private(self):
        assert not is_private(name="test")
        assert is_private(name="_test")
        assert is_private(name="__test")

    def test_match_visibility(self):
        assert match_visibility(name="test", visibility="public")
        assert match_visibility(name="_test", visibility="private")
        assert match_visibility(name="__test", visibility="private")

    def test_runtime_checkable(self):
        class Test:
            name: str

        t = Test()
        assert isinstance(t, Test)
        assert not isinstance(t, Named), "a name must be valued"

        t.name = "hello"
        assert isinstance(t, Named)
