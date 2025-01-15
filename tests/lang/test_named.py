from sumps.lang.named import is_private, is_public, match_visibility
from tests.conftest import parametrize


@parametrize(
    "obj,is_func",
    [
        ("test", is_public),
        ("_test", is_private),
        ("__test", is_private),
    ],
)
def test_is(obj, is_func):
    assert is_func(name=obj)


@parametrize(
    "name,visibility",
    [
        ("test", "public"),
        ("_test", "private"),
        ("__test", "private"),
    ],
)
def test_match_visibility(name, visibility):
    assert match_visibility(name=name, visibility=visibility)
