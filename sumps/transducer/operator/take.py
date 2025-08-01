"""Take transducers for limiting items from the beginning."""

from __future__ import annotations
from ..base import BaseTransducer, Transducer, Reduced, BaseAsyncTransducer, AsyncTransducer, Result, Input

__all__ = ["Take", "take", "AsyncTake", "atake"]


class Take[Result, Input](BaseTransducer[Result, Input]):
    """Transducer that takes only the first n items.
    
    Processes items until the limit is reached, then terminates early
    using the Reduced wrapper to signal completion.
    
    Edge cases:
    - limit <= 0: No items taken, immediate termination
    - limit > input size: All items taken
    - Empty input: No items taken
    
    Args:
        reducer: Wrapped reducer that processes taken items
        limit: Maximum number of items to take
        
    Example:
        >>> take3 = take(3)(appending())
        >>> transduce(identity, [1, 2, 3, 4, 5], take3)  # [1, 2, 3]
        >>> take0 = take(0)(appending())
        >>> transduce(identity, [1, 2, 3], take0)  # []
    """
    
    def __init__(self, reducer: Transducer[Result, Input], limit: int):
        self._reducer = reducer
        self._limit = limit
        self._counter = 0

    def initial(self) -> Result:
        """Reset counter and delegate to wrapped reducer."""
        self._counter = 0
        return self._reducer.initial()

    def step(self, result: Result, item: Input) -> Result:
        """Take item if under limit, terminate when limit reached."""
        if self._limit <= 0:
            return Reduced(result)  # type: ignore
        self._counter += 1
        value = self._reducer.step(result, item)
        return value if self._counter < self._limit else Reduced(value) # type: ignore

    def complete(self, result: Result) -> Result:
        """Complete reduction with wrapped reducer."""
        return self._reducer.complete(result)


def take(limit: int):
    """Create a transducer that takes only the first n items."""
    def take_transducer(reducer: Transducer[Result, Input]) -> Take[Result, Input]:
        return Take(reducer, limit)
    return take_transducer


class AsyncTake[Result, Input](BaseAsyncTransducer[Result, Input]):
    """Async transducer that takes only the first n items.
    
    Async version of Take that works with async transducer pipelines.
    
    Example:
        >>> import asyncio
        >>> async def example():
        ...     result = await atransduce(
        ...         atake(3),
        ...         async_from_iterable([1, 2, 3, 4, 5]),
        ...         aappending()
        ...     )
        ...     return result  # [1, 2, 3]
        >>> asyncio.run(example())
    """
    
    def __init__(self, reducer: AsyncTransducer[Result, Input], limit: int):
        self._reducer = reducer
        self._limit = limit
        self._counter = 0

    async def initial(self) -> Result:
        """Reset counter and delegate to wrapped reducer."""
        self._counter = 0
        return await self._reducer.initial()

    async def step(self, result: Result, item: Input) -> Result:
        """Take item if under limit, terminate when limit reached."""
        if self._limit <= 0:
            return Reduced(result)  # type: ignore
        self._counter += 1
        value = await self._reducer.step(result, item)
        return value if self._counter < self._limit else Reduced(value) # type: ignore

    async def complete(self, result: Result) -> Result:
        """Complete reduction with wrapped reducer."""
        return await self._reducer.complete(result)


def atake(limit: int):
    """Create an async transducer that takes only the first n items.
    
    Example:
        >>> import asyncio
        >>> async def example():
        ...     result = await atransduce(
        ...         atake(2),
        ...         async_from_iterable([1, 2, 3, 4]),
        ...         aappending()
        ...     )
        ...     return result  # [1, 2]
        >>> asyncio.run(example())
    """
    def atake_transducer(reducer: AsyncTransducer[Result, Input]) -> AsyncTake[Result, Input]:
        return AsyncTake(reducer, limit)
    return atake_transducer