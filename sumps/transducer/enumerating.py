from .model import Transducer

__all__ = ["enumerating"]


class Enumerating(Transducer):
    """Enumerate item to (index, item)."""

    def __init__(self, reducer: Transducer, start: int = 0):
        self._reducer = reducer
        self._start = start
        self._counter = start

    def initial(self):
        self._counter = self._start
        return self._reducer.initial()

    def step(self, result, item):
        index = self._counter
        self._counter += 1
        return self._reducer.step(result, (index, item))

    def complete(self, result):
        return self._reducer.complete(result)


def enumerating(start: int = 0):
    """Create a transducer which enumerates items."""

    def enumerating_transducer(reducer):
        return Enumerating(reducer=reducer, start=start)

    return enumerating_transducer
