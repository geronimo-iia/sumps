from sumps.lang import singleton


@singleton
class CounterDecorated:
    def __init__(self):
        self.count = 0

    def inc(self):
        self.count += 1


def test_singleton():
    a = CounterDecorated()
    b = CounterDecorated()
    assert a != b  # shared state did not mean shared instance
    assert a.count == b.count
    a.inc()
    assert a.count == b.count
    b.inc()
    assert a.count == b.count == 2
