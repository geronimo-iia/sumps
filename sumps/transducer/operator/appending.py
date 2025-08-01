"""Appending reducer for collecting items into lists."""

from __future__ import annotations
from ..base import BaseTransducer, BaseAsyncTransducer, BaseAsyncTransducer
from typing import Any

__all__ = ["Appending", "appending", "AsyncAppending", "aappending"]


class Appending[T](BaseTransducer[list[T], T]):
    """Transducer that collects items into a list.
    
    Accumulates items by appending them to a mutable list. This is the most
    common reducer for collecting transduced results.
    
    Edge cases:
    - Empty input: Returns empty list
    - Memory efficient: Mutates result list in-place
    
    Example:
        >>> reducer = appending()
        >>> result = reducer.initial()  # []
        >>> result = reducer.step(result, 1)  # [1]
        >>> result = reducer.step(result, 2)  # [1, 2]
        >>> final = reducer.complete(result)  # [1, 2]
    """
    
    def initial(self) -> list[T]:
        """Return empty list as initial accumulator."""
        return []

    def step(self, result: list[T], item: T) -> list[T]:
        """Append item to result list in-place.
        
        Args:
            result: Current list accumulator
            item: Item to append
            
        Returns:
            The same list with item appended
        """
        result.append(item)
        return result

    def complete(self, result: list[T]) -> list[T]:
        """Return final list result unchanged.
        
        Args:
            result: Final accumulated list
            
        Returns:
            The completed list
        """
        return result


def appending() -> Appending[Any]:
    """Create an appending reducer that collects items into a list.
    
    This is the default reducer used by transduce() when no reducer is specified.
    
    Returns:
        Appending transducer instance
        
    Example:
        >>> from sumps.transducer import transduce, mapping, appending
        >>> result = transduce(mapping(str.upper), ['a', 'b'], appending())
        >>> result  # ['A', 'B']
    """
    return Appending()


class AsyncAppending[T](BaseAsyncTransducer[list[T], T]):
    """Async transducer that collects items into a list.
    
    Async version of Appending that works with async transducer pipelines.
    
    Example:
        >>> import asyncio
        >>> async def example():
        ...     result = await atransduce(
        ...         async_mapping(lambda x: x * 2),
        ...         async_from_iterable([1, 2, 3]),
        ...         aappending()
        ...     )
        ...     return result  # [2, 4, 6]
        >>> asyncio.run(example())
    """
    
    async def initial(self) -> list[T]:
        """Return empty list as initial accumulator."""
        return []

    async def step(self, result: list[T], item: T) -> list[T]:
        """Append item to result list in-place."""
        result.append(item)
        return result

    async def complete(self, result: list[T]) -> list[T]:
        """Return final list result unchanged."""
        return result


def aappending() -> AsyncAppending[Any]:
    """Create an async appending reducer that collects items into a list.
    
    This is the default async reducer used by atransduce() when no reducer is specified.
    
    Returns:
        AsyncAppending transducer instance
        
    Example:
        >>> import asyncio
        >>> async def example():
        ...     result = await atransduce(
        ...         async_mapping(str.upper), 
        ...         async_from_iterable(['a', 'b']), 
        ...         aappending()
        ...     )
        ...     return result  # ['A', 'B']
        >>> asyncio.run(example())
    """
    return AsyncAppending()