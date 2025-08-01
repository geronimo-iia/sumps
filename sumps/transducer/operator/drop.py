"""Drop transducer for skipping items from the beginning."""

from __future__ import annotations
from ..base import BaseTransducer, Transducer, BaseAsyncTransducer, AsyncTransducer, Result, Input

__all__ = ["Drop", "drop", "AsyncDrop", "adrop"]


class Drop[Result, Input](BaseTransducer[Result, Input]):
    """Transducer that drops the first n items.
    
    Ignores the first n items, then processes all subsequent items normally.
    
    Edge cases:
    - limit <= 0: No items dropped, all items pass through
    - limit >= input size: All items dropped
    - Empty input: No items to drop
    
    Args:
        reducer: Wrapped reducer that processes remaining items
        limit: Number of items to drop from the beginning
        
    Example:
        >>> drop2 = drop(2)(appending())
        >>> transduce(identity, [1, 2, 3, 4, 5], drop2)  # [3, 4, 5]
        >>> drop0 = drop(0)(appending())
        >>> transduce(identity, [1, 2], drop0)  # [1, 2]
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
        """Drop item if under limit, process normally afterwards."""
        if self._counter < self._limit:
            self._counter += 1
            return result
        return self._reducer.step(result, item)

    def complete(self, result: Result) -> Result:
        """Complete reduction with wrapped reducer."""
        return self._reducer.complete(result)


def drop(limit: int):
    """Create a transducer that drops the first n items."""
    def drop_transducer(reducer: Transducer[Result, Input]) -> Drop[Result, Input]:
        return Drop(reducer, limit)
    return drop_transducer


class AsyncDrop[Result, Input](BaseAsyncTransducer[Result, Input]):
    """Async transducer that drops the first n items.
    
    Async version of Drop that works with async transducer pipelines.
    
    Example:
        >>> import asyncio
        >>> async def example():
        ...     result = await atransduce(
        ...         adrop(2),
        ...         async_from_iterable([1, 2, 3, 4, 5]),
        ...         aappending()
        ...     )
        ...     return result  # [3, 4, 5]
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
        """Drop item if under limit, process normally afterwards."""
        if self._counter < self._limit:
            self._counter += 1
            return result
        return await self._reducer.step(result, item)

    async def complete(self, result: Result) -> Result:
        """Complete reduction with wrapped reducer."""
        return await self._reducer.complete(result)


def adrop(limit: int):
    """Create an async transducer that drops the first n items.
    
    Example:
        >>> import asyncio
        >>> async def example():
        ...     result = await atransduce(
        ...         adrop(3),
        ...         async_from_iterable([1, 2, 3, 4, 5, 6]),
        ...         aappending()
        ...     )
        ...     return result  # [4, 5, 6]
        >>> asyncio.run(example())
    """
    def adrop_transducer(reducer: AsyncTransducer[Result, Input]) -> AsyncDrop[Result, Input]:
        return AsyncDrop(reducer, limit)
    return adrop_transducer