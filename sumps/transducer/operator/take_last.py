"""TakeLast reducer for keeping items from the end."""

from __future__ import annotations
from ..base import BaseTransducer, Transducer, BaseAsyncTransducer, AsyncTransducer, SizedResult

__all__ = ["TakeLast", "take_last", "AsyncTakeLast", "atake_last"]


class TakeLast[Input](BaseTransducer[SizedResult, Input]):
    """Transducer that keeps only the last n items from the result.
    
    Collects all items during processing, then keeps only the specified number
    of items from the end during completion. Only works with sized, sliceable
    result types (lists, tuples, strings, etc.).
    
    Edge cases:
    - limit <= 0: Returns empty result of same type
    - limit >= result size: Returns all items unchanged
    - Non-sliceable results: Falls back to wrapped reducer completion
    - TypeError/AttributeError: Gracefully falls back to original result
    
    Args:
        reducer: Wrapped reducer that produces sized results
        limit: Number of items to keep from the end
        
    Example:
        >>> take2 = take_last(2)(appending())
        >>> transduce(identity, [1, 2, 3, 4, 5], take2)  # [4, 5]
        >>> transduce(identity, [1], take2)  # [1]
        >>> transduce(identity, [], take2)  # []
    """

    def __init__(self, reducer: Transducer[SizedResult, Input], limit: int):
        self._reducer = reducer
        self._limit = limit

    def initial(self) -> SizedResult:
        """Delegate to wrapped reducer for initial value."""
        return self._reducer.initial()

    def step(self, result: SizedResult, item: Input) -> SizedResult:
        """Delegate to wrapped reducer for item processing."""
        return self._reducer.step(result, item)

    def complete(self, result: SizedResult) -> SizedResult:
        """Keep only last n items from result before completion.
        
        Args:
            result: Accumulated sized result
            
        Returns:
            Result with only last n items, completed by wrapped reducer
            
        Note:
            Falls back to original result if slicing operations fail
        """
        try:
            size = len(result)
            if self._limit <= 0:
                empty = result[:0] if hasattr(result, '__getitem__') else self._reducer.initial()
                return self._reducer.complete(empty)
            if size >= self._limit:
                sliced = result[size - self._limit :]
                return self._reducer.complete(sliced)
            return self._reducer.complete(result)
        except (TypeError, AttributeError) as e:
            # Fallback if result doesn't support expected operations
            return self._reducer.complete(result)


def take_last[Input](limit: int):
    """Create a transducer that keeps only the last n items from results.
    
    Returns a function that wraps a reducer to keep only the specified number
    of items from the end of the accumulated result.
    
    Args:
        limit: Number of items to keep from the end (must be >= 0)
        
    Returns:
        Function that takes a reducer and returns TakeLast wrapper
        
    Example:
        >>> from sumps.transducer import transduce, take_last, appending
        >>> take_2 = take_last(2)
        >>> result = transduce(identity, [1, 2, 3, 4, 5], take_2(appending()))
        >>> result  # [4, 5]
    """
    def take_last_transducer(reducer: Transducer[SizedResult, Input]) -> TakeLast[Input]:
        return TakeLast(reducer, limit)

    return take_last_transducer


class AsyncTakeLast[Input](BaseAsyncTransducer[SizedResult, Input]):
    """Async transducer that keeps only the last n items from the result.
    
    Async version of TakeLast that works with async transducer pipelines.
    
    Example:
        >>> import asyncio
        >>> async def example():
        ...     result = await atransduce(
        ...         atake_last(2),
        ...         async_from_iterable([1, 2, 3, 4, 5]),
        ...         aappending()
        ...     )
        ...     return result  # [4, 5]
        >>> asyncio.run(example())
    """

    def __init__(self, reducer: AsyncTransducer[SizedResult, Input], limit: int):
        self._reducer = reducer
        self._limit = limit

    async def initial(self) -> SizedResult:
        """Delegate to wrapped reducer for initial value."""
        return await self._reducer.initial()

    async def step(self, result: SizedResult, item: Input) -> SizedResult:
        """Delegate to wrapped reducer for item processing."""
        return await self._reducer.step(result, item)

    async def complete(self, result: SizedResult) -> SizedResult:
        """Keep only last n items from result before completion."""
        try:
            size = len(result)
            if self._limit <= 0:
                empty = result[:0] if hasattr(result, '__getitem__') else await self._reducer.initial()
                return await self._reducer.complete(empty)
            if size >= self._limit:
                sliced = result[size - self._limit :]
                return await self._reducer.complete(sliced)
            return await self._reducer.complete(result)
        except (TypeError, AttributeError):
            return await self._reducer.complete(result)


def atake_last[Input](limit: int):
    """Create an async transducer that keeps only the last n items from results.
    
    Example:
        >>> import asyncio
        >>> async def example():
        ...     result = await atransduce(
        ...         atake_last(3),
        ...         async_from_iterable([1, 2, 3, 4, 5, 6]),
        ...         aappending()
        ...     )
        ...     return result  # [4, 5, 6]
        >>> asyncio.run(example())
    """
    def atake_last_transducer(reducer: AsyncTransducer[SizedResult, Input]) -> AsyncTakeLast[Input]:
        return AsyncTakeLast(reducer, limit)
    return atake_last_transducer