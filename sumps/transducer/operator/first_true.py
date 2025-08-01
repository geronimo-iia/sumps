"""FirstTrue transducer for taking the first matching item."""

from __future__ import annotations
from ..base import BaseTransducer, Transducer, Predicate, Reduced, BaseAsyncTransducer, AsyncTransducer, Result, Input
from typing import Callable, Awaitable

__all__ = ["FirstTrue", "first_true", "AsyncFirstTrue", "afirst_true"]


class FirstTrue[Result, Input](BaseTransducer[Result, Input]):
    """Transducer that takes the first item matching a predicate.
    
    Processes items until one matches the predicate, then terminates early.
    If no predicate is provided, takes the first truthy item.
    
    Edge cases:
    - No items match: No items taken
    - First item matches: Only first item taken
    - Empty input: No items taken
    - Predicate is None: Uses truthiness test
    
    Args:
        reducer: Wrapped reducer that processes the matching item
        predicate: Function to test items, or None for truthiness
        
    Example:
        >>> is_even = lambda x: x % 2 == 0
        >>> first_even = first_true(is_even)(appending())
        >>> transduce(identity, [1, 3, 4, 6], first_even)  # [4]
        >>> first_truthy = first_true()(appending())
        >>> transduce(identity, [0, '', 'hi'], first_truthy)  # ['hi']
    """
    
    def __init__(self, reducer: Transducer[Result, Input], predicate: Predicate[Input]):
        self._reducer = reducer
        self._predicate = predicate

    def initial(self) -> Result:
        """Delegate to wrapped reducer for initial value."""
        return self._reducer.initial()

    def step(self, result: Result, item: Input) -> Result:
        """Take item if predicate matches, terminate immediately."""
        return Reduced(self._reducer.step(result, item)) if self._predicate(item) else result  # type: ignore

    def complete(self, result: Result) -> Result:
        """Complete reduction with wrapped reducer."""
        return self._reducer.complete(result)


def first_true[Input](predicate: Predicate[Input] | None = None):
    """Create a transducer that takes the first item matching a predicate."""
    def _true(item) -> bool:
        return bool(item)
    
    predicate = _true if predicate is None else predicate
    
    def first_true_transducer(reducer: Transducer[Result, Input]) -> FirstTrue[Result, Input]:
        return FirstTrue(reducer, predicate)
    return first_true_transducer


class AsyncFirstTrue[Result, Input](BaseAsyncTransducer[Result, Input]):
    """Async transducer that takes the first item matching a predicate.
    
    Async version of FirstTrue that works with async transducer pipelines.
    
    Example:
        >>> import asyncio
        >>> async def example():
        ...     result = await atransduce(
        ...         afirst_true(lambda x: x > 3),
        ...         async_from_iterable([1, 2, 4, 5]),
        ...         aappending()
        ...     )
        ...     return result  # [4]
        >>> asyncio.run(example())
    """
    
    def __init__(self, reducer: AsyncTransducer[Result, Input], predicate: Callable[[Input], Awaitable[bool]] | Predicate[Input]):
        self._reducer = reducer
        self._predicate = predicate

    async def initial(self) -> Result:
        """Delegate to wrapped reducer for initial value."""
        return await self._reducer.initial()

    async def step(self, result: Result, item: Input) -> Result:
        """Take item if predicate matches, terminate immediately."""
        try:
            should_include = await self._predicate(item)  # type: ignore
        except TypeError:
            should_include = self._predicate(item)  # type: ignore
        
        return Reduced(await self._reducer.step(result, item)) if should_include else result  # type: ignore

    async def complete(self, result: Result) -> Result:
        """Complete reduction with wrapped reducer."""
        return await self._reducer.complete(result)


def afirst_true[Input](predicate: Callable[[Input], Awaitable[bool]] | Predicate[Input] | None = None):
    """Create an async transducer that takes the first item matching a predicate.
    
    Example:
        >>> import asyncio
        >>> async def example():
        ...     result = await atransduce(
        ...         afirst_true(lambda x: x % 2 == 0),
        ...         async_from_iterable([1, 3, 4, 6]),
        ...         aappending()
        ...     )
        ...     return result  # [4]
        >>> asyncio.run(example())
    """
    def _true(item) -> bool:
        return bool(item)
    
    predicate = _true if predicate is None else predicate
    
    def afirst_true_transducer(reducer: AsyncTransducer[Result, Input]) -> AsyncFirstTrue[Result, Input]:
        return AsyncFirstTrue(reducer, predicate)
    return afirst_true_transducer