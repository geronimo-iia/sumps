"""Batching transducer for grouping items into fixed-size batches."""

from __future__ import annotations
from ..base import BaseTransducer, Transducer, BaseAsyncTransducer, AsyncTransducer, Result, Input
from typing import Any

__all__ = ["Batching", "batching", "AsyncBatching", "abatching"]


class Batching[Result, Input](BaseTransducer[Result, Input]):
    """Transducer that groups items into fixed-size batches.
    
    Collects items into batches of the specified size and emits complete batches
    to the wrapped reducer. The final incomplete batch (if any) is emitted during
    completion.
    
    Edge cases:
    - size < 1: Raises ValueError during construction
    - Empty input: No batches emitted
    - Incomplete final batch: Emitted during completion
    - Single item batches: Each item becomes a single-element batch
    
    Args:
        reducer: Wrapped reducer that processes batches
        size: Number of items per batch (must be >= 1)
        
    Raises:
        ValueError: If size < 1
        
    Example:
        >>> batch3 = batching(3)(appending())
        >>> transduce(identity, [1, 2, 3, 4, 5], batch3)  # [[1, 2, 3], [4, 5]]
        >>> transduce(identity, [1, 2, 3], batch3)  # [[1, 2, 3]]
        >>> transduce(identity, [], batch3)  # []
    """
    
    def __init__(self, reducer: Transducer[Result, Input], size: int):
        if size < 1:
            raise ValueError("batching() size must be at least 1")
        self._reducer = reducer
        self._size = size
        self._pending: list[Input] = []

    def initial(self) -> Result:
        """Initialize empty pending batch and delegate to wrapped reducer."""
        self._pending = []
        return self._reducer.initial()

    def step(self, result: Result, item: Input) -> Result:
        """Add item to pending batch, emit when full.
        
        Args:
            result: Current accumulator
            item: Item to add to current batch
            
        Returns:
            Updated result, potentially with new batch processed
        """
        self._pending.append(item)
        if len(self._pending) == self._size:
            batch = self._pending
            self._pending = []
            return self._reducer.step(result, batch)  # type: ignore
        return result

    def complete(self, result: Result) -> Result:
        """Emit final incomplete batch (if any) and complete.
        
        Args:
            result: Final accumulator
            
        Returns:
            Completed result from wrapped reducer
        """
        if self._pending:
            result = self._reducer.step(result, self._pending)  # type: ignore
        return self._reducer.complete(result)


def batching(size: int):
    """Create a transducer that groups items into fixed-size batches.
    
    Returns a function that wraps a reducer to collect items into batches
    of the specified size. Complete batches are emitted immediately, and
    any incomplete final batch is emitted during completion.
    
    Args:
        size: Number of items per batch (must be >= 1)
        
    Returns:
        Function that takes a reducer and returns Batching wrapper
        
    Raises:
        ValueError: If size < 1
        
    Example:
        >>> from sumps.transducer import transduce, batching, appending
        >>> batch_2 = batching(2)
        >>> result = transduce(identity, [1, 2, 3, 4, 5], batch_2(appending()))
        >>> result  # [[1, 2], [3, 4], [5]]
    """
    def batching_transducer(reducer: Transducer[Result, Input]) -> Batching[Result, Input]:
        return Batching(reducer, size)

    return batching_transducer


class AsyncBatching[Result, Input](BaseAsyncTransducer[Result, Input]):
    """Async transducer that groups items into fixed-size batches.
    
    Async version of Batching that works with async transducer pipelines.
    
    Example:
        >>> import asyncio
        >>> async def example():
        ...     result = await atransduce(
        ...         abatching(3),
        ...         async_from_iterable([1, 2, 3, 4, 5]),
        ...         aappending()
        ...     )
        ...     return result  # [[1, 2, 3], [4, 5]]
        >>> asyncio.run(example())
    """
    
    def __init__(self, reducer: AsyncTransducer[Result, Input], size: int):
        if size < 1:
            raise ValueError("abatching() size must be at least 1")
        self._reducer = reducer
        self._size = size
        self._pending: list[Input] = []

    async def initial(self) -> Result:
        """Initialize empty pending batch and delegate to wrapped reducer."""
        self._pending = []
        return await self._reducer.initial()

    async def step(self, result: Result, item: Input) -> Result:
        """Add item to pending batch, emit when full."""
        self._pending.append(item)
        if len(self._pending) == self._size:
            batch = self._pending
            self._pending = []
            return await self._reducer.step(result, batch)  # type: ignore
        return result

    async def complete(self, result: Result) -> Result:
        """Emit final incomplete batch (if any) and complete."""
        if self._pending:
            result = await self._reducer.step(result, self._pending)  # type: ignore
        return await self._reducer.complete(result)


def abatching(size: int):
    """Create an async transducer that groups items into fixed-size batches.
    
    Args:
        size: Number of items per batch (must be >= 1)
        
    Returns:
        Function that takes an async reducer and returns AsyncBatching wrapper
        
    Example:
        >>> import asyncio
        >>> async def example():
        ...     result = await atransduce(
        ...         abatching(2),
        ...         async_from_iterable([1, 2, 3, 4, 5]),
        ...         aappending()
        ...     )
        ...     return result  # [[1, 2], [3, 4], [5]]
        >>> asyncio.run(example())
    """
    def abatching_transducer(reducer: AsyncTransducer[Result, Input]) -> AsyncBatching[Result, Input]:
        return AsyncBatching(reducer, size)
    return abatching_transducer