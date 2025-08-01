"""Singleton design pattern revisited.

See http://code.activestate.com/recipes/66531-singleton-we-dont-need-no-stinkin-singleton-the-bo/

'The Borg design pattern has all instances share state ...' it's similar to Monostate pattern alias singleton.

Use case:
 You want do instantiate a class from anywhere in your program AND get access to the same data.

Usage:

    @singleton
    class CounterDecorated:
        def __init__(self):
            self.count = 0

        def inc(self):
            self.count += 1


    a = CounterDecorated()
    a.inc()
    assert a.count == 1

    b = CounterDecorated()
    assert a.count == b.count == 1


"""

from typing import TypeVar

T = TypeVar("T")


__all__ = ["singleton"]


def singleton(cls: type[T]) -> type[T]:
    """Singleton class decorator using Borg/Monostate pattern.

    All instances share the same state dictionary.

    Original author: Max Egger.

    Change:
        - call original init only once.

    Usage:

        @singleton
        class Foo(object):
            def say_hello(self):
                print "hello, I'm a borg"

        @singleton
        class CounterDecorated:
            def __init__(self):
                self.count = 0

            def inc(self):
                self.count += 1


    """
    cls.__shared_state = {}  # type: ignore

    orig_init = cls.__init__

    def new_init(self, *args, **kwargs):
        nonlocal orig_init
        # Redirect instance __dict__ to shared state dict
        self.__dict__ = cls.__shared_state  # type: ignore
        # Call original __init__ only once
        if orig_init is not None:
            orig_init(self, *args, **kwargs)
            orig_init = None

    cls.__init__ = new_init

    return cls
