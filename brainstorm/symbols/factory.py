from collections.abc import Callable
from typing import TypeVar

__all__ = ["factory"]

T = TypeVar("T")


def factory(cls: type[T]) -> Callable[[], T]:
    return lambda: cls()
