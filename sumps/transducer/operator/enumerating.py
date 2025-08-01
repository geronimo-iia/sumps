"""Enumerating transducer for adding indices to items."""

from __future__ import annotations
from ..base import BaseTransducer, Transducer, BaseAsyncTransducer, AsyncTransducer, Result, Input

__all__ = ["Enumerating", "enumerating", "AsyncEnumerating", "aenumerating"]


class Enumerating[Result, Input](BaseTransducer[Result, Input]):
    """Transducer that enumerates items with indices.
    
    Transforms each item into a tuple of (index, item), similar to Python's
    built-in enumerate() function. The index starts from the specified value
    and increments for each item.
    
    Edge cases:
    - Empty input: No items enumerated, counter remains at start value
    - start value: Can be any integer (positive, negative, or zero)
    - Counter state: Maintained across step calls, reset on initial()
    
    Args:
        reducer: Wrapped reducer that processes (index, item) tuples
        start: Starting index value (default: 0)
        
    Example:
        >>> enum_from_1 = enumerating(1)(appending())
        >>> transduce(identity, ['a', 'b', 'c'], enum_from_1)  # [(1, 'a'), (2, 'b'), (3, 'c')]
        >>> enum_default = enumerating()(appending())
        >>> transduce(identity, ['x', 'y'], enum_default)  # [(0, 'x'), (1, 'y')]
    """
    
    def __init__(self, reducer: Transducer[Result, Input], start: int = 0):
        self._reducer = reducer
        self._start = start
        self._counter = start

    def initial(self) -> Result:
        """Reset counter to start value and delegate to wrapped reducer."""
        self._counter = self._start
        return self._reducer.initial()

    def step(self, result: Result, item: Input) -> Result:
        """Enumerate item with current index and increment counter.
        
        Args:
            result: Current accumulator
            item: Item to enumerate
            
        Returns:
            Result after processing (index, item) tuple
        """
        index = self._counter
        self._counter += 1
        return self._reducer.step(result, (index, item))  # type: ignore

    def complete(self, result: Result) -> Result:
        """Complete reduction with wrapped reducer.
        
        Args:
            result: Final accumulator
            
        Returns:
            Completed result from wrapped reducer
        """
        return self._reducer.complete(result)


def enumerating(start: int = 0):
    """Create a transducer that enumerates items with indices.
    
    Returns a function that wraps a reducer to transform each item into
    a tuple of (index, item), starting from the specified index.
    
    Args:
        start: Starting index value (default: 0)
        
    Returns:
        Function that takes a reducer and returns Enumerating wrapper
        
    Example:
        >>> from sumps.transducer import transduce, enumerating, appending
        >>> enum_from_10 = enumerating(10)
        >>> result = transduce(identity, ['a', 'b'], enum_from_10(appending()))
        >>> result  # [(10, 'a'), (11, 'b')]
    """
    def enumerating_transducer(reducer: Transducer[Result, Input]) -> Enumerating[Result, Input]:
        return Enumerating(reducer, start)

    return enumerating_transducer


class AsyncEnumerating[Result, Input](BaseAsyncTransducer[Result, Input]):
    """Async transducer that enumerates items with indices.
    
    Async version of Enumerating that works with async transducer pipelines.
    
    Example:
        >>> import asyncio
        >>> async def example():
        ...     result = await atransduce(
        ...         aenumerating(1),
        ...         async_from_iterable(['a', 'b', 'c']),
        ...         aappending()
        ...     )
        ...     return result  # [(1, 'a'), (2, 'b'), (3, 'c')]
        >>> asyncio.run(example())
    """
    
    def __init__(self, reducer: AsyncTransducer[Result, Input], start: int = 0):
        self._reducer = reducer
        self._start = start
        self._counter = start

    async def initial(self) -> Result:
        """Reset counter to start value and delegate to wrapped reducer."""
        self._counter = self._start
        return await self._reducer.initial()

    async def step(self, result: Result, item: Input) -> Result:
        """Enumerate item with current index and increment counter."""
        index = self._counter
        self._counter += 1
        return await self._reducer.step(result, (index, item))  # type: ignore

    async def complete(self, result: Result) -> Result:
        """Complete reduction with wrapped reducer."""
        return await self._reducer.complete(result)


def aenumerating(start: int = 0):
    """Create an async transducer that enumerates items with indices.
    
    Example:
        >>> import asyncio
        >>> async def example():
        ...     result = await atransduce(
        ...         aenumerating(10),
        ...         async_from_iterable(['x', 'y']),
        ...         aappending()
        ...     )
        ...     return result  # [(10, 'x'), (11, 'y')]
        >>> asyncio.run(example())
    """
    def aenumerating_transducer(reducer: AsyncTransducer[Result, Input]) -> AsyncEnumerating[Result, Input]:
        return AsyncEnumerating(reducer, start)
    return aenumerating_transducer