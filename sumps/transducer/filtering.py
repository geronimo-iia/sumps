from .model import Predicate, Transducer

__all__ = ["filtering"]


class Filtering(Transducer):
    def __init__(self, reducer: Transducer, predicate: Predicate):
        self._reducer = reducer
        self._predicate = predicate

    def initial(self):
        return self._reducer.initial()

    def step(self, result, item):
        return self._reducer.step(result, item) if self._predicate(item) else result

    def complete(self, result):
        return self._reducer.complete(result)


def filtering(predicate: Predicate):
    def filtering_transducer(reducer: Transducer):
        return Filtering(reducer=reducer, predicate=predicate)

    return filtering_transducer
