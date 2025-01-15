from __future__ import annotations

from collections.abc import Callable
from typing import Any, Protocol, TypeVar, runtime_checkable

__all__ = [
    "Predicate",
    "Transform",
    "Transducer",
    "Reduced",
    "is_reducer",
]

Result = TypeVar("Result")
Input = TypeVar("Input")

type Reducing[Result, Input] = Callable[[Result, Input], Result]

type Predicate[Input] = Callable[[Input], bool]

type Transform[Input, Result] = Callable[[Input], Result]


@runtime_checkable
class Transducer(Protocol):
    def initial(self) -> Any: ...  # Return the initial seed value

    def step(self, result, item) -> Any: ...  # Next step in the reduction

    def complete(self, result) -> Any: ...  # Produce a final result and clean up


def is_reducer(obj: Any) -> bool:
    return isinstance(obj, Transducer)


class Reduced:
    """A sentinel 'box' used to return the final value of a reduction."""

    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value
