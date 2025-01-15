from .model import Transducer

__all__ = ["appending", "conjoining", "expecting_single", "drop_last", "take_last"]


class Appending(Transducer):
    def initial(self):
        return []

    def step(self, result, item):
        result.append(item)
        return result

    def complete(self, result):
        return result


def appending():
    return Appending()


class Conjoining(Transducer):
    def initial(self):
        return ()

    def step(self, result, item):
        return result + type(result)((item,))

    def complete(self, result):
        return result


def conjoining():
    return Conjoining()


class ExpectingSingle(Transducer):
    def __init__(self, reducer: Transducer):
        self._reducer = reducer
        self._num_steps = 0

    def initial(self):
        self._num_steps = 0
        return self._reducer.initial()

    def step(self, result, item):
        self._num_steps += 1
        if self._num_steps > 1:
            raise RuntimeError("Too many steps!")
        return self._reducer.step(result=result, item=item)

    def complete(self, result):
        if self._num_steps < 1:
            raise RuntimeError("Too few steps!")
        return self._reducer.complete(result=result)


def expecting_single():
    def expecting_single_transducer(reducer):
        return ExpectingSingle(reducer=reducer)

    return expecting_single_transducer


class DropLast(Transducer):
    """Keeps items from origin except last n."""

    def __init__(self, reducer: Transducer, limit: int):
        self._reducer = reducer
        self._limit = limit

    def initial(self):
        return self._reducer.initial()

    def step(self, result, item):
        return self._reducer.step(result, item)

    def complete(self, result: list | tuple):
        size = len(result)
        if size >= self._limit:
            return result[0 : size - self._limit]
        return [] if isinstance(self._reducer, Appending) else ()


def drop_last(limit: int):
    def drop_last_transducer(reducer):
        return DropLast(reducer=reducer, limit=limit)

    return drop_last_transducer


class TakeLast(Transducer):
    """Keeps items last n."""

    def __init__(self, reducer: Transducer, limit: int):
        self._reducer = reducer
        self._limit = limit

    def initial(self):
        return self._reducer.initial()

    def step(self, result, item):
        return self._reducer.step(result, item)

    def complete(self, result: list | tuple):
        size = len(result)
        if size >= self._limit:
            return result[size - self._limit :]
        return result


def take_last(limit: int):
    def take_last_transducer(reducer):
        return TakeLast(reducer=reducer, limit=limit)

    return take_last_transducer
