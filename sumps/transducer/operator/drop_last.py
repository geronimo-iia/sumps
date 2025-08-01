"""DropLast reducer for removing items from the end."""

from __future__ import annotations
from ..base import BaseTransducer, Transducer, BaseAsyncTransducer, AsyncTransducer, SizedResult

__all__ = ["DropLast", "drop_last", "AsyncDropLast", "adrop_last"]


class DropLast[Input](BaseTransducer[SizedResult, Input]):
    """Transducer that removes the last n items from the result.
    
    Collects all items during processing, then removes the specified number
    of items from the end during completion. Only works with sized, sliceable
    result types (lists, tuples, strings, etc.).
    
    Edge cases:
    - limit <= 0: Returns all items unchanged
    - limit >= result size: Returns empty result of same type
    - Non-sliceable results: Falls back to wrapped reducer completion
    - TypeError/AttributeError: Gracefully falls back to original result
    
    Args:
        reducer: Wrapped reducer that produces sized results
        limit: Number of items to drop from the end
        
    Example:
        >>> drop2 = drop_last(2)(appending())
        >>> transduce(identity, [1, 2, 3, 4, 5], drop2)  # [1, 2, 3]
        >>> transduce(identity, [1], drop2)  # []
        >>> transduce(identity, [], drop2)  # []
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
        """Remove last n items from result before completion.
        
        Args:
            result: Accumulated sized result
            
        Returns:
            Result with last n items removed, completed by wrapped reducer
            
        Note:
            Falls back to original result if slicing operations fail
        """
        try:
            size = len(result)
            if self._limit <= 0:
                return self._reducer.complete(result)
            if size > self._limit:
                sliced = result[0 : size - self._limit]
                return self._reducer.complete(sliced)
            # If size <= limit, return empty result of same type
            empty = result[:0] if hasattr(result, '__getitem__') else self._reducer.initial()
            return self._reducer.complete(empty)
        except (TypeError, AttributeError) as e:
            # Fallback if result doesn't support expected operations
            return self._reducer.complete(result)


def drop_last[Input](limit: int):
    """Create a transducer that drops the last n items from results.
    
    Returns a function that wraps a reducer to remove the specified number
    of items from the end of the accumulated result.
    
    Args:
        limit: Number of items to drop from the end (must be >= 0)
        
    Returns:
        Function that takes a reducer and returns DropLast wrapper
        
    Example:
        >>> from sumps.transducer import transduce, drop_last, appending
        >>> drop_2 = drop_last(2)
        >>> result = transduce(identity, [1, 2, 3, 4, 5], drop_2(appending()))
        >>> result  # [1, 2, 3]
    """
    def drop_last_transducer(reducer: Transducer[SizedResult, Input]) -> DropLast[Input]:
        return DropLast(reducer, limit)

    return drop_last_transducer


class AsyncDropLast[Input](BaseAsyncTransducer[SizedResult, Input]):
    """Async transducer that removes the last n items from the result.
    
    Async version of DropLast that works with async transducer pipelines.
    
    Example:
        >>> import asyncio
        >>> async def example():
        ...     result = await atransduce(
        ...         adrop_last(2),
        ...         async_from_iterable([1, 2, 3, 4, 5]),
        ...         aappending()
        ...     )
        ...     return result  # [1, 2, 3]
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
        """Remove last n items from result before completion."""
        try:
            size = len(result)
            if self._limit <= 0:
                return await self._reducer.complete(result)
            if size > self._limit:
                sliced = result[0 : size - self._limit]
                return await self._reducer.complete(sliced)
            empty = result[:0] if hasattr(result, '__getitem__') else await self._reducer.initial()
            return await self._reducer.complete(empty)
        except (TypeError, AttributeError):
            return await self._reducer.complete(result)


def adrop_last[Input](limit: int):
    """Create an async transducer that drops the last n items from results.
    
    Example:
        >>> import asyncio
        >>> async def example():
        ...     result = await atransduce(
        ...         adrop_last(1),
        ...         async_from_iterable([1, 2, 3, 4]),
        ...         aappending()
        ...     )
        ...     return result  # [1, 2, 3]
        >>> asyncio.run(example())
    """
    def adrop_last_transducer(reducer: AsyncTransducer[SizedResult, Input]) -> AsyncDropLast[Input]:
        return AsyncDropLast(reducer, limit)
    return adrop_last_transducer