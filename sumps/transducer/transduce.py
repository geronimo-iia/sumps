from collections.abc import Callable, Iterable
from typing import Any

from .model import Reduced, Transducer
from .reducer import appending

__all__ = ["transduce"]

_UNSET = object()


def transduce(
    transducer: Callable[[Transducer], Transducer],
    iterable: Iterable[Any],
    reducer: Transducer | None = None,
    init=_UNSET,
):
    reducer = reducer if reducer else appending()
    r = transducer(reducer)
    accumulator = init if (init is not _UNSET) else r.initial()
    for item in iterable:
        accumulator = r.step(accumulator, item)
        if isinstance(accumulator, Reduced):
            accumulator = accumulator.value
            break
    return r.complete(accumulator)
