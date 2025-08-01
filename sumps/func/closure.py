"""Closure module."""

from collections.abc import Callable
from functools import wraps

from sumps.aio import iscoroutinefunction

__all__ = ["closure"]


def closure(decorated: Callable):
    """Transform any function to a generator of function which have only closed term.
    This is a pattern that I use very often to build a composition of function.


    Example:

    ```
    @closure
    async def source(producer: Callable[[], Awaitable], output_channel: Channel):
        while True:
            value = await producer()
            await output_channel.send(value=value)
    ```

    could be wrote like that:

    ```
    async def source(producer: Callable[[], Awaitable], output_channel: Channel):
        async def _source():
            while True:
                value = await producer()
                await output_channel.send(value=value)

        return _source
    ```

    Usage:
    ```
    @closure
    async def source(producer: Callable[[], Awaitable], output_channel: Channel):
        while True:
            value = await producer()
            await output_channel.send(value=value)


    my_source = await source(producer=..., output_channel=...)

    # excute the inner loop
    await my_source()
    ```

    Args:
        decorated (Callable): a function (sync or async) to transform in an builder of clojure.
    """
    if not iscoroutinefunction(decorated):

        @wraps(decorated)
        def awrapper(*args, **kwargs):
            @wraps(decorated)
            def _fn():
                return decorated(*args, **kwargs)

            return _fn

        return awrapper

    # return an async wrapper
    @wraps(decorated)
    async def wrapper(*args, **kwargs):
        @wraps(decorated)
        async def _fn():
            return await decorated(*args, **kwargs)

        return _fn

    return wrapper
