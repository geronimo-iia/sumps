"""Nth transducer for taking a specific positioned item."""

from __future__ import annotations
from ..base import BaseTransducer, Transducer, Reduced, BaseAsyncTransducer, AsyncTransducer, Result, Input
from typing import Any

__all__ = ["Nth", "nth", "AsyncNth", "anth"]


class Nth[Result, Input](BaseTransducer[Result, Input]):
    """Transducer that takes only the nth item (1-indexed).
    
    Counts items until the nth position is reached, takes that item,
    then terminates. If fewer than n items exist, uses the default value.
    
    Edge cases:
    - n <= 0: No items taken, uses default
    - n > input size: Uses default value
    - Empty input: Uses default value
    - default is None: None is used as fallback
    
    Args:
        reducer: Wrapped reducer that processes the nth item or default
        n: Position of item to take (1-indexed)
        default: Value to use if nth item doesn't exist
        
    Example:
        >>> nth3 = nth(3, 'missing')(appending())
        >>> transduce(identity, [1, 2, 3, 4], nth3)  # [3]
        >>> transduce(identity, [1, 2], nth3)  # ['missing']
        >>> nth1 = nth(1)(appending())
        >>> transduce(identity, ['a', 'b'], nth1)  # ['a']
    """
    
    def __init__(self, reducer: Transducer[Result, Input], n: int, default: Any):
        self._reducer = reducer
        self._n = n
        self._counter = 0
        self._default = default

    def initial(self) -> Result:
        """Reset counter and delegate to wrapped reducer."""
        self._counter = 0
        return self._reducer.initial()

    def step(self, result: Result, item: Input) -> Result:
        """Count items until nth position, take that item and terminate."""
        self._counter += 1
        if self._counter == self._n:
            return Reduced(self._reducer.step(result, item))  # type: ignore
        return result

    def complete(self, result: Result) -> Result:
        """Complete with nth item if found, otherwise with default."""
        if self._counter < self._n:
            result = self._reducer.step(result, self._default)
        return self._reducer.complete(result)


def nth(n: int, default: Any = None):
    """Create a transducer that takes only the nth item (1-indexed)."""
    def nth_transducer(reducer: Transducer[Result, Input]) -> Nth[Result, Input]:
        return Nth(reducer, n, default)
    return nth_transducer


class AsyncNth[Result, Input](BaseAsyncTransducer[Result, Input]):
    """Async transducer that takes only the nth item (1-indexed).
    
    Async version of Nth that works with async transducer pipelines.
    
    Example:
        >>> import asyncio
        >>> async def example():
        ...     result = await atransduce(
        ...         anth(3, 'missing'),
        ...         async_from_iterable(['a', 'b', 'c', 'd']),
        ...         aappending()
        ...     )
        ...     return result  # ['c']
        >>> asyncio.run(example())
    """
    
    def __init__(self, reducer: AsyncTransducer[Result, Input], n: int, default: Any):
        self._reducer = reducer
        self._n = n
        self._counter = 0
        self._default = default

    async def initial(self) -> Result:
        """Reset counter and delegate to wrapped reducer."""
        self._counter = 0
        return await self._reducer.initial()

    async def step(self, result: Result, item: Input) -> Result:
        """Count items until nth position, take that item and terminate."""
        self._counter += 1
        if self._counter == self._n:
            return Reduced(await self._reducer.step(result, item))  # type: ignore
        return result

    async def complete(self, result: Result) -> Result:
        """Complete with nth item if found, otherwise with default."""
        if self._counter < self._n:
            result = await self._reducer.step(result, self._default)
        return await self._reducer.complete(result)


def anth(n: int, default: Any = None):
    """Create an async transducer that takes only the nth item (1-indexed).
    
    Example:
        >>> import asyncio
        >>> async def example():
        ...     result = await atransduce(
        ...         anth(2, 'default'),
        ...         async_from_iterable(['first']),
        ...         aappending()
        ...     )
        ...     return result  # ['default']
        >>> asyncio.run(example())
    """
    def anth_transducer(reducer: AsyncTransducer[Result, Input]) -> AsyncNth[Result, Input]:
        return AsyncNth(reducer, n, default)
    return anth_transducer