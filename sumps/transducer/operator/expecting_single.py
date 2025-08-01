"""ExpectingSingle reducer for enforcing single-item processing."""

from __future__ import annotations
from ..base import BaseTransducer, Transducer, BaseAsyncTransducer, AsyncTransducer

__all__ = ["ExpectingSingle", "expecting_single", "AsyncExpectingSingle", "aexpecting_single"]


class ExpectingSingle[Result, Input](BaseTransducer[Result, Input]):
    """Transducer wrapper that enforces exactly one item processing.
    
    Validates that exactly one item is processed during the reduction.
    Useful for operations that should only work on single-item sequences.
    
    Edge cases:
    - Zero items: Raises RuntimeError("Too few steps!")
    - Multiple items: Raises RuntimeError("Too many steps!")
    - Exactly one item: Processes normally
    
    Args:
        reducer: Wrapped transducer to delegate to
        
    Raises:
        RuntimeError: If zero or more than one items are processed
        
    Example:
        >>> single = expecting_single()(appending())
        >>> # Works with one item
        >>> transduce(identity, [42], single)  # [42]
        >>> # Fails with multiple items
        >>> transduce(identity, [1, 2], single)  # RuntimeError
    """
    
    def __init__(self, reducer: Transducer[Result, Input]):
        self._reducer = reducer
        self._num_steps = 0

    def initial(self) -> Result:
        """Initialize step counter and delegate to wrapped reducer."""
        self._num_steps = 0
        return self._reducer.initial()

    def step(self, result: Result, item: Input) -> Result:
        """Process item if it's the first, otherwise raise error.
        
        Args:
            result: Current accumulator
            item: Item to process
            
        Returns:
            Result from wrapped reducer
            
        Raises:
            RuntimeError: If more than one item is processed
        """
        self._num_steps += 1
        if self._num_steps > 1:
            raise RuntimeError("Too many steps!")
        return self._reducer.step(result, item)

    def complete(self, result: Result) -> Result:
        """Complete reduction if exactly one item was processed.
        
        Args:
            result: Final accumulator
            
        Returns:
            Completed result from wrapped reducer
            
        Raises:
            RuntimeError: If zero items were processed
        """
        if self._num_steps < 1:
            raise RuntimeError("Too few steps!")
        return self._reducer.complete(result)


def expecting_single[Result, Input]():
    """Create a transducer that enforces exactly one item processing.
    
    Returns a function that wraps another reducer to ensure exactly one
    item is processed during the reduction.
    
    Returns:
        Function that takes a reducer and returns ExpectingSingle wrapper
        
    Example:
        >>> from sumps.transducer import transduce, expecting_single, appending
        >>> single_reducer = expecting_single()(appending())
        >>> result = transduce(identity, [42], single_reducer)  # [42]
        >>> # This would raise: transduce(identity, [1, 2], single_reducer)
    """
    def expecting_single_transducer(reducer: Transducer[Result, Input]) -> ExpectingSingle[Result, Input]:
        return ExpectingSingle(reducer)

    return expecting_single_transducer


class AsyncExpectingSingle[Result, Input](BaseAsyncTransducer[Result, Input]):
    """Async transducer wrapper that enforces exactly one item processing.
    
    Async version of ExpectingSingle that works with async transducer pipelines.
    
    Example:
        >>> import asyncio
        >>> async def example():
        ...     result = await atransduce(
        ...         aexpecting_single(),
        ...         async_from_iterable([42]),
        ...         aappending()
        ...     )
        ...     return result  # [42]
        >>> asyncio.run(example())
    """
    
    def __init__(self, reducer: AsyncTransducer[Result, Input]):
        self._reducer = reducer
        self._num_steps = 0

    async def initial(self) -> Result:
        """Initialize step counter and delegate to wrapped reducer."""
        self._num_steps = 0
        return await self._reducer.initial()

    async def step(self, result: Result, item: Input) -> Result:
        """Process item if it's the first, otherwise raise error."""
        self._num_steps += 1
        if self._num_steps > 1:
            raise RuntimeError("Too many steps!")
        return await self._reducer.step(result, item)

    async def complete(self, result: Result) -> Result:
        """Complete reduction if exactly one item was processed."""
        if self._num_steps < 1:
            raise RuntimeError("Too few steps!")
        return await self._reducer.complete(result)


def aexpecting_single[Result, Input]():
    """Create an async transducer that enforces exactly one item processing.
    
    Example:
        >>> import asyncio
        >>> async def example():
        ...     result = await atransduce(
        ...         aexpecting_single(),
        ...         async_from_iterable(['single']),
        ...         aappending()
        ...     )
        ...     return result  # ['single']
        >>> asyncio.run(example())
    """
    def aexpecting_single_transducer(reducer: AsyncTransducer[Result, Input]) -> AsyncExpectingSingle[Result, Input]:
        return AsyncExpectingSingle(reducer)
    return aexpecting_single_transducer