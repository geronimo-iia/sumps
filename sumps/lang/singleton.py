"""Singleton design pattern revisited.

See http://code.activestate.com/recipes/66531-singleton-we-dont-need-no-stinkin-singleton-the-bo/

'The Borg design pattern has all instances share state ...' it's similar to Monostate pattern alias singleton.

Use case:
 You want do instantiate a class from anywhere in your program AND get access to the same data.


Example:
```
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
```

"""

__all__ = ["singleton"]


def singleton(cls):
    """singleton class decorator.

    Original author: Max Egger.

    Change:
        - call original init only once.

    Example:
    ```
    @singleton
    class Foo(object):
        def say_hello(self):
            print "hello, I'm a borg"
    ```

    or

    ```
    @singleton
    class CounterDecorated:
        def __init__(self):
            self.count = 0

        def inc(self):
            self.count += 1
    ```

    """
    cls.__shared_state = {}

    orig_init = cls.__init__

    def new_init(self, *args, **kwargs):
        nonlocal orig_init
        self.__dict__ = cls.__shared_state
        if orig_init:  # call only once
            orig_init(self, *args, **kwargs)
            orig_init = None

    cls.__init__ = new_init

    return cls
