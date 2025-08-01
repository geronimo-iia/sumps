import pytest

from sumps.lang.registry import Dictionary, Named, RegisterHandler, Registry


# Minimal Named implementation for testing
class NamedTest(Named):
    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name


def test_dictionary_add_and_exists():
    d = Dictionary[NamedTest]()
    item = NamedTest("foo")
    assert not d.exists("foo")
    d.add(item)
    assert d.exists("foo")
    assert next(d.all()).name == "foo"


def test_dictionary_remove():
    d = Dictionary[NamedTest]()
    item = NamedTest("foo")
    d.add(item)
    removed = d.remove("foo")
    assert removed is item
    assert not d.exists("foo")
    with pytest.raises(KeyError):
        d.remove("foo")


def test_dictionary_freeze_and_add_remove():
    d = Dictionary[NamedTest]()
    d.add(NamedTest("foo"))
    d.freeze()
    with pytest.raises(RuntimeError):
        d.add(NamedTest("bar"))
    with pytest.raises(RuntimeError):
        d.remove("foo")
    assert d.frozen() is True


def test_dictionary_filter():
    d = Dictionary[NamedTest]()
    d.add(NamedTest("foo"))
    d.add(NamedTest("_bar"))
    # Using match_visibility function logic
    public_items = list(d.filter("public"))
    private_items = list(d.filter("private"))
    assert any(item.name == "foo" for item in public_items)
    assert all(item.name.startswith("_") for item in private_items)


def test_registry_handler_add():
    r = Registry[NamedTest]()
    handler: RegisterHandler[NamedTest] = r.handler()
    item = NamedTest("foo")
    handler(item)
    assert r.exists("foo")


def test_registry_inherits_dictionary_methods():
    r = Registry[NamedTest]()
    item = NamedTest("foo")
    r.add(item)
    assert r.exists("foo")
    removed = r.remove("foo")
    assert removed is item
    assert not r.exists("foo")


def test_all_method_yields_items():
    d = Dictionary[NamedTest]()
    items = [NamedTest("a"), NamedTest("b"), NamedTest("c")]
    for i in items:
        d.add(i)
    all_items = list(d.all())
    assert set(i.name for i in all_items) == {"a", "b", "c"}
