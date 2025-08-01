"""Filtering transducer for selecting items based on predicates."""

from __future__ import annotations
from ..base import BaseTransducer, Transducer, Predicate, BaseAsyncTransducer, AsyncTransducer, Result, Input
from typing import Callable, Awaitable

__all__ = ["Filtering", "filtering", "AsyncFiltering", "afiltering"]


class Filtering[Result, Input](BaseTransducer[Result, Input]):
    """Transducer that filters items based on a predicate function.
    
    Only items for which the predicate returns a truthy value are passed
    to the wrapped reducer. Items that don't match are ignored.
    
    Edge cases:
    - Empty input: No items filtered
    - All items match: All items pass through
    - No items match: No items passed to reducer
    - Predicate raises exception: Exception propagates up
    
    Args:
        reducer: Wrapped reducer that processes filtered items
        predicate: Function that takes an item and returns bool-like value
        
    Example:
        >>> is_even = lambda x: x % 2 == 0
        >>> filter_even = filtering(is_even)(appending())
        >>> transduce(identity, [1, 2, 3, 4, 5], filter_even)  # [2, 4]
        >>> filter_truthy = filtering(bool)(appending())
        >>> transduce(identity, [0, 1, '', 'hi', None], filter_truthy)  # [1, 'hi']
    """
    
    def __init__(self, reducer: Transducer[Result, Input], predicate: Predicate[Input]):
        self._reducer = reducer
        self._predicate = predicate

    def initial(self) -> Result:
        """Delegate to wrapped reducer for initial value."""
        return self._reducer.initial()

    def step(self, result: Result, item: Input) -> Result:
        """Filter item through predicate before processing.
        
        Args:
            result: Current accumulator
            item: Item to potentially filter
            
        Returns:
            Updated result if item passes predicate, unchanged otherwise
        """
        return self._reducer.step(result, item) if self._predicate(item) else result

    def complete(self, result: Result) -> Result:
        """Complete reduction with wrapped reducer.
        
        Args:
            result: Final accumulator
            
        Returns:
            Completed result from wrapped reducer
        """
        return self._reducer.complete(result)


def filtering(predicate: Predicate[Input]):
    """Create a transducer that filters items based on a predicate.
    
    Returns a function that wraps a reducer to only process items
    for which the predicate returns a truthy value.
    
    Args:
        predicate: Function that takes an item and returns bool-like value
        
    Returns:
        Function that takes a reducer and returns Filtering wrapper
        
    Example:
        >>> from sumps.transducer import transduce, filtering, appending
        >>> is_positive = lambda x: x > 0
        >>> filter_pos = filtering(is_positive)
        >>> result = transduce(identity, [-1, 0, 1, 2], filter_pos(appending()))
        >>> result  # [1, 2]
    """
    def filtering_transducer(reducer: Transducer[Result, Input]) -> Filtering[Result, Input]:
        return Filtering(reducer, predicate)

    return filtering_transducer


class AsyncFiltering[Result, Input](BaseAsyncTransducer[Result, Input]):
    """Async transducer that filters items based on an async predicate function.
    
    Only items for which the predicate returns a truthy value are passed
    to the wrapped reducer. Supports both sync and async predicates.
    
    Example:
        >>> async def is_even_async(x):
        ...     await asyncio.sleep(0.01)  # Simulate async work
        ...     return x % 2 == 0
        >>> async_filter = afiltering(is_even_async)
    """
    
    def __init__(self, reducer: AsyncTransducer[Result, Input], predicate: Callable[[Input], Awaitable[bool]] | Predicate[Input]):
        self._reducer = reducer
        self._predicate = predicate

    async def initial(self) -> Result:
        """Delegate to wrapped reducer for initial value."""
        return await self._reducer.initial()

    async def step(self, result: Result, item: Input) -> Result:
        """Filter item through predicate before processing."""
        try:
            # Try async call first
            should_include = await self._predicate(item)  # type: ignore
        except TypeError:
            # Fall back to sync call
            should_include = self._predicate(item)  # type: ignore
        
        if should_include:
            return await self._reducer.step(result, item)
        return result

    async def complete(self, result: Result) -> Result:
        """Complete reduction with wrapped reducer."""
        return await self._reducer.complete(result)


def afiltering[Input](predicate: Callable[[Input], Awaitable[bool]] | Predicate[Input]):
    """Create an async transducer that filters items based on a predicate.
    
    Returns a function that wraps an async reducer to only process items
    for which the predicate returns a truthy value. Supports both sync and async predicates.
    
    Args:
        predicate: Function that takes an item and returns bool-like value
        
    Returns:
        Function that takes an async reducer and returns AsyncFiltering wrapper
        
    Example:
        >>> async def is_positive_async(x):
        ...     await asyncio.sleep(0.01)
        ...     return x > 0
        >>> async_filter_pos = afiltering(is_positive_async)
        >>> result = await atransduce(async_filter_pos, async_range(-2, 3), aappending())
        >>> result  # [1, 2]
    """
    def afiltering_transducer(reducer: AsyncTransducer[Result, Input]) -> AsyncFiltering[Result, Input]:
        return AsyncFiltering(reducer, predicate)
    return afiltering_transducer