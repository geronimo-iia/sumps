from .model import Transducer

__all__ = ["repeating"]


class Repeating(Transducer):
    def __init__(self, reducer: Transducer, num_times: int):
        self._reducer = reducer
        self._num_times = num_times

    def initial(self):
        return self._reducer.initial()

    def step(self, result, item):
        for _ in range(self._num_times):
            result = self._reducer.step(result, item)
        return result

    def complete(self, result):
        return self._reducer.complete(result)


def repeating(num_times: int):
    if num_times < 0:
        raise ValueError("num_times cannot be negative")

    def repeating_transducer(reducer):
        return Repeating(reducer=reducer, num_times=num_times)

    return repeating_transducer
