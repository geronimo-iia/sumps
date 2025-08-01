"""Conjoining reducer for collecting items into tuples."""

from __future__ import annotations
from ..base import BaseTransducer, BaseAsyncTransducer
from typing import Any

__all__ = ["Conjoining", "conjoining", "AsyncConjoining", "aconjoining"]


class Conjoining[T](BaseTransducer[tuple[T, ...], T]):
    """Transducer that collects items into a tuple.
    
    Accumulates items by creating new tuples (immutable). Less memory efficient
    than appending but produces immutable results.
    
    Edge cases:
    - Empty input: Returns empty tuple
    - Memory overhead: Creates new tuple for each item
    
    Example:
        >>> reducer = conjoining()
        >>> result = reducer.initial()  # ()
        >>> result = reducer.step(result, 1)  # (1,)
        >>> result = reducer.step(result, 2)  # (1, 2)
        >>> final = reducer.complete(result)  # (1, 2)
    """
    
    def initial(self) -> tuple[T, ...]:
        """Return empty tuple as initial accumulator."""
        return ()

    def step(self, result: tuple[T, ...], item: T) -> tuple[T, ...]:
        """Create new tuple with item appended.
        
        Args:
            result: Current tuple accumulator
            item: Item to append
            
        Returns:
            New tuple with item appended
        """
        return result + (item,)

    def complete(self, result: tuple[T, ...]) -> tuple[T, ...]:
        """Return final tuple result unchanged.
        
        Args:
            result: Final accumulated tuple
            
        Returns:
            The completed tuple
        """
        return result


def conjoining() -> Conjoining[Any]:
    """Create a conjoining reducer that collects items into a tuple.
    
    Useful when you need immutable results or when working with functional
    programming patterns that prefer immutable data structures.
    
    Returns:
        Conjoining transducer instance
        
    Example:
        >>> from sumps.transducer import transduce, mapping, conjoining
        >>> result = transduce(mapping(str.upper), ['a', 'b'], conjoining())
        >>> result  # ('A', 'B')
    """
    return Conjoining()


class AsyncConjoining[T](BaseAsyncTransducer[tuple[T, ...], T]):
    """Async transducer that collects items into a tuple.
    
    Async version of Conjoining that works with async transducer pipelines.
    
    Example:
        >>> import asyncio
        >>> async def example():
        ...     result = await atransduce(
        ...         async_mapping(str.upper),
        ...         async_from_iterable(['a', 'b', 'c']),
        ...         aconjoining()
        ...     )
        ...     return result  # ('A', 'B', 'C')
        >>> asyncio.run(example())
    """
    
    async def initial(self) -> tuple[T, ...]:
        """Return empty tuple as initial accumulator."""
        return ()

    async def step(self, result: tuple[T, ...], item: T) -> tuple[T, ...]:
        """Create new tuple with item appended."""
        return result + (item,)

    async def complete(self, result: tuple[T, ...]) -> tuple[T, ...]:
        """Return final tuple result unchanged."""
        return result


def aconjoining() -> AsyncConjoining[Any]:
    """Create an async conjoining reducer that collects items into a tuple.
    
    Returns:
        AsyncConjoining transducer instance
        
    Example:
        >>> import asyncio
        >>> async def example():
        ...     result = await atransduce(
        ...         async_mapping(lambda x: x * 2),
        ...         async_from_iterable([1, 2, 3]),
        ...         aconjoining()
        ...     )
        ...     return result  # (2, 4, 6)
        >>> asyncio.run(example())
    """
    return AsyncConjoining()