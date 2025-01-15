from .model import Transducer, Transform

__all__ = ["mapping"]


class Mapping(Transducer):
    def __init__(self, reducer: Transducer, transform: Transform):
        self._reducer = reducer
        self._transform = transform

    def initial(self):
        return self._reducer.initial()

    def step(self, result, item):
        return self._reducer.step(result, self._transform(item))

    def complete(self, result):
        return self._reducer.complete(result)


def mapping(transform: Transform):
    def mapping_transducer(reducer: Transducer):
        return Mapping(reducer=reducer, transform=transform)

    return mapping_transducer
