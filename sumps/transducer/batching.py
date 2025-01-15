from .model import Transducer

__all__ = ["batching"]


class Batching(Transducer):
    def __init__(self, reducer: Transducer, size: int):
        self._reducer = reducer
        self._size = size
        self._pending = []

    def initial(self):
        self._pending = []
        return self._reducer.initial()

    def step(self, result, item):
        self._pending.append(item)
        if len(self._pending) == self._size:
            batch = self._pending
            self._pending = []
            return self._reducer.step(result, batch)
        return result

    def complete(self, result):
        r = self._reducer.step(result, self._pending) if len(self._pending) > 0 else result
        return self._reducer.complete(r)


def batching(size: int):
    """Create a transducer which produces non-overlapping batches."""

    if size < 1:
        raise ValueError("batching() size must be at least 1")

    def batching_transducer(reducer):
        return Batching(reducer=reducer, size=size)

    return batching_transducer
