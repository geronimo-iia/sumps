"""Repeating transducer for duplicating items multiple times."""

from __future__ import annotations
from ..base import BaseTransducer, Transducer, BaseAsyncTransducer, AsyncTransducer, Result, Input

__all__ = ["Repeating", "repeating", "AsyncRepeating", "arepeating"]


class Repeating[Result, Input](BaseTransducer[Result, Input]):
    """Transducer that repeats each item a specified number of times.
    
    Each input item is passed to the wrapped reducer multiple times in sequence.
    Useful for duplicating items or amplifying signals.
    
    Edge cases:
    - num_times = 0: Items are ignored (not passed to reducer)
    - num_times = 1: Items pass through unchanged
    - num_times < 0: Raises ValueError during construction
    - Empty input: No items repeated
    
    Args:
        reducer: Wrapped reducer that processes repeated items
        num_times: Number of times to repeat each item (must be >= 0)
        
    Raises:
        ValueError: If num_times < 0
        
    Example:
        >>> repeat3 = repeating(3)(appending())
        >>> transduce(identity, [1, 2], repeat3)  # [1, 1, 1, 2, 2, 2]
        >>> repeat0 = repeating(0)(appending())
        >>> transduce(identity, [1, 2], repeat0)  # []
    """
    
    def __init__(self, reducer: Transducer[Result, Input], num_times: int):
        if num_times < 0:
            raise ValueError("num_times cannot be negative")
        self._reducer = reducer
        self._num_times = num_times

    def initial(self) -> Result:
        """Delegate to wrapped reducer for initial value."""
        return self._reducer.initial()

    def step(self, result: Result, item: Input) -> Result:
        """Repeat item num_times to wrapped reducer.
        
        Args:
            result: Current accumulator
            item: Item to repeat
            
        Returns:
            Result after processing item num_times
        """
        for _ in range(self._num_times):
            result = self._reducer.step(result, item)
        return result

    def complete(self, result: Result) -> Result:
        """Complete reduction with wrapped reducer.
        
        Args:
            result: Final accumulator
            
        Returns:
            Completed result from wrapped reducer
        """
        return self._reducer.complete(result)


def repeating(num_times: int):
    """Create a transducer that repeats each item multiple times.
    
    Returns a function that wraps a reducer to repeat each input item
    the specified number of times.
    
    Args:
        num_times: Number of times to repeat each item (must be >= 0)
        
    Returns:
        Function that takes a reducer and returns Repeating wrapper
        
    Raises:
        ValueError: If num_times < 0
        
    Example:
        >>> from sumps.transducer import transduce, repeating, appending
        >>> repeat_2 = repeating(2)
        >>> result = transduce(identity, [1, 2, 3], repeat_2(appending()))
        >>> result  # [1, 1, 2, 2, 3, 3]
    """
    def repeating_transducer(reducer: Transducer[Result, Input]) -> Repeating[Result, Input]:
        return Repeating(reducer, num_times)

    return repeating_transducer


class AsyncRepeating[Result, Input](BaseAsyncTransducer[Result, Input]):
    """Async transducer that repeats each item a specified number of times.
    
    Async version of Repeating that works with async transducer pipelines.
    
    Example:
        >>> import asyncio
        >>> async def example():
        ...     result = await atransduce(
        ...         arepeating(3),
        ...         async_from_iterable([1, 2]),
        ...         aappending()
        ...     )
        ...     return result  # [1, 1, 1, 2, 2, 2]
        >>> asyncio.run(example())
    """
    
    def __init__(self, reducer: AsyncTransducer[Result, Input], num_times: int):
        if num_times < 0:
            raise ValueError("num_times cannot be negative")
        self._reducer = reducer
        self._num_times = num_times

    async def initial(self) -> Result:
        """Delegate to wrapped reducer for initial value."""
        return await self._reducer.initial()

    async def step(self, result: Result, item: Input) -> Result:
        """Repeat item num_times to wrapped reducer."""
        for _ in range(self._num_times):
            result = await self._reducer.step(result, item)
        return result

    async def complete(self, result: Result) -> Result:
        """Complete reduction with wrapped reducer."""
        return await self._reducer.complete(result)


def arepeating(num_times: int):
    """Create an async transducer that repeats each item multiple times.
    
    Example:
        >>> import asyncio
        >>> async def example():
        ...     result = await atransduce(
        ...         arepeating(2),
        ...         async_from_iterable(['a', 'b']),
        ...         aappending()
        ...     )
        ...     return result  # ['a', 'a', 'b', 'b']
        >>> asyncio.run(example())
    """
    def arepeating_transducer(reducer: AsyncTransducer[Result, Input]) -> AsyncRepeating[Result, Input]:
        return AsyncRepeating(reducer, num_times)
    return arepeating_transducer