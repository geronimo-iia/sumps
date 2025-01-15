from .model import Predicate, Reduced, Transducer

__all__ = ["first_true", "take", "drop", "nth"]


class Take(Transducer):
    """Take first #limit items."""

    def __init__(self, reducer: Transducer, limit: int):
        self._reducer = reducer
        self._limit = limit
        self._counter = 0

    def initial(self):
        self._counter = 0
        return self._reducer.initial()

    def step(self, result, item):
        self._counter += 1
        value = self._reducer.step(result, item)
        return value if self._counter < self._limit else Reduced(value=value)

    def complete(self, result):
        return self._reducer.complete(result)


def take(limit: int):
    def take_transducer(reducer):
        return Take(reducer=reducer, limit=limit)

    return take_transducer


class FirstTrue(Transducer):
    """Take first item where predicate is True."""

    def __init__(self, reducer: Transducer, predicate: Predicate):
        self._reducer = reducer
        self._predicate = predicate

    def initial(self):
        return self._reducer.initial()

    def step(self, result, item):
        return Reduced(self._reducer.step(result, item)) if self._predicate(item) else result

    def complete(self, result):
        return self._reducer.complete(result)


def first_true(predicate: Predicate | None = None):
    def _true(item) -> bool:
        return bool(item)

    predicate = _true if predicate is None else predicate

    def first_true_transducer(reducer):
        return FirstTrue(reducer, predicate)

    return first_true_transducer


class Drop(Transducer):
    """Drops first #limit items."""

    def __init__(self, reducer: Transducer, limit: int):
        self._reducer = reducer
        self._limit = limit
        self._counter = 0

    def initial(self):
        self._counter = 0
        return self._reducer.initial()

    def step(self, result, item):
        if self._counter < self._limit:
            self._counter += 1
            return result
        return self._reducer.step(result, item)

    def complete(self, result):
        return self._reducer.complete(result)


def drop(limit: int):
    def drop_transducer(reducer):
        return Drop(reducer=reducer, limit=limit)

    return drop_transducer


class Nth(Transducer):
    """Take nth items or a default value."""

    def __init__(self, reducer: Transducer, n: int, default):
        self._reducer = reducer
        self._n = n
        self._counter = 0
        self._default = default

    def initial(self):
        self._counter = 0
        return self._reducer.initial()

    def step(self, result, item):
        self._counter += 1
        if self._counter == self._n:
            return Reduced(self._reducer.step(result, item))
        # ignore
        return result

    def complete(self, result):
        if self._counter == self._n:
            return self._reducer.complete(result=result)
        return self._reducer.complete(result=self._default)


def nth(n: int, default=None):
    def nth_transducer(reducer):
        return Nth(reducer=reducer, n=n, default=default)

    return nth_transducer
