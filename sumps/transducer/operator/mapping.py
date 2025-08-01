"""Mapping transducer for transforming items."""

from __future__ import annotations
from ..base import BaseTransducer, Transducer, Transform, Result, Input, BaseAsyncTransducer, AsyncTransducer
from typing import TypeVar, Callable, Awaitable

__all__ = ["Mapping", "mapping", "AsyncMapping", "async_mapping"]

Output = TypeVar('Output')


class Mapping[Result, Input, Output](BaseTransducer[Result, Input]):
    """Transducer that transforms items using a transform function.
    
    Applies the transform function to each item before passing it to the
    wrapped reducer. This is the transducer equivalent of map().
    
    Edge cases:
    - Empty input: No items transformed
    - Transform raises exception: Exception propagates up
    - Transform returns None: None is passed to reducer
    - Identity transform: Items pass through unchanged
    
    Args:
        reducer: Wrapped reducer that processes transformed items
        transform: Function that transforms input items to output items
        
    Example:
        >>> double = lambda x: x * 2
        >>> map_double = mapping(double)(appending())
        >>> transduce(identity, [1, 2, 3], map_double)  # [2, 4, 6]
        >>> to_upper = mapping(str.upper)(appending())
        >>> transduce(identity, ['a', 'b'], to_upper)  # ['A', 'B']
    """
    
    def __init__(self, reducer: Transducer[Result, Output], transform: Transform[Input, Output]):
        self._reducer = reducer
        self._transform = transform

    def initial(self) -> Result:
        """Delegate to wrapped reducer for initial value."""
        return self._reducer.initial()

    def step(self, result: Result, item: Input) -> Result:
        """Transform item before passing to wrapped reducer.
        
        Args:
            result: Current accumulator
            item: Item to transform
            
        Returns:
            Result after processing transformed item
        """
        return self._reducer.step(result, self._transform(item))

    def complete(self, result: Result) -> Result:
        """Complete reduction with wrapped reducer.
        
        Args:
            result: Final accumulator
            
        Returns:
            Completed result from wrapped reducer
        """
        return self._reducer.complete(result)


def mapping[Input, Output](transform: Transform[Input, Output]):
    """Create a transducer that transforms items using a function.
    
    Returns a function that wraps a reducer to apply the transform function
    to each item before processing.
    
    Args:
        transform: Function that transforms input items to output items
        
    Returns:
        Function that takes a reducer and returns Mapping wrapper
        
    Example:
        >>> from sumps.transducer import transduce, mapping, appending
        >>> square = lambda x: x ** 2
        >>> map_square = mapping(square)
        >>> result = transduce(identity, [1, 2, 3, 4], map_square(appending()))
        >>> result  # [1, 4, 9, 16]
    """
    def mapping_transducer(reducer: Transducer[Result, Output]) -> Mapping[Result, Input, Output]:
        return Mapping(reducer, transform)

    return mapping_transducer


class AsyncMapping[Result, Input, Output](BaseAsyncTransducer[Result, Input]):
    """Async transducer that transforms items using an async transform function.
    
    Applies an async transform function to each item before passing it to the
    wrapped reducer. Supports both sync and async transform functions.
    
    Example:
        >>> async def async_double(x):
        ...     await asyncio.sleep(0.01)  # Simulate async work
        ...     return x * 2
        >>> async_map = async_mapping(async_double)
    """
    
    def __init__(self, reducer: AsyncTransducer[Result, Output], transform: Callable[[Input], Awaitable[Output]] | Callable[[Input], Output]):
        self._reducer = reducer
        self._transform = transform

    async def initial(self) -> Result:
        """Delegate to wrapped reducer for initial value."""
        return await self._reducer.initial()

    async def step(self, result: Result, item: Input) -> Result:
        """Transform item (possibly async) before passing to wrapped reducer."""
        try:
            # Try async call first
            transformed = await self._transform(item)  # type: ignore
        except TypeError:
            # Fall back to sync call
            transformed = self._transform(item)  # type: ignore
        
        return await self._reducer.step(result, transformed)  # type: ignore

    async def complete(self, result: Result) -> Result:
        """Complete reduction with wrapped reducer."""
        return await self._reducer.complete(result)


def async_mapping[Input, Output](transform: Callable[[Input], Awaitable[Output]] | Callable[[Input], Output]):
    """Create an async transducer that transforms items using a function.
    
    Returns a function that wraps an async reducer to apply the transform function
    to each item before processing. Supports both sync and async transform functions.
    
    Args:
        transform: Function that transforms input items to output items
        
    Returns:
        Function that takes an async reducer and returns AsyncMapping wrapper
        
    Example:
        >>> async def async_square(x):
        ...     await asyncio.sleep(0.01)
        ...     return x ** 2
        >>> async_map_square = async_mapping(async_square)
        >>> result = await atransduce(async_map_square, async_range(4), aappending())
        >>> result  # [0, 1, 4, 9]
    """
    def async_mapping_transducer(reducer: AsyncTransducer[Result, Output]) -> AsyncMapping[Result, Input, Output]:
        return AsyncMapping(reducer, transform)
    return async_mapping_transducer