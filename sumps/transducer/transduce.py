"""Core transduction function for efficient data processing pipelines."""

from __future__ import annotations
from collections.abc import Callable, Iterable, AsyncIterable
from typing import Any, TypeVar, cast

from .base import Reduced, Transducer, AsyncTransducer
from .operator import appending

__all__ = ["transduce", "atransduce"]

T = TypeVar('T')
U = TypeVar('U')
_UNSET = object()


def transduce(
    transducer: Callable[[Transducer[T, U]], Transducer[T, Any]],
    iterable: Iterable[Any],
    reducer: Transducer[T, U] | None = None,
    init: T = _UNSET,
) -> T:
    """Execute a transduction pipeline on an iterable.
    
    Applies a transducer transformation to an iterable, collecting results
    using the specified reducer. This is the main entry point for transducer
    processing pipelines.
    
    Args:
        transducer: Function that transforms a reducer into a new reducer.
                   Can be a single transducer or a composition of multiple
                   transducers using function composition or the | operator.
        iterable: Input data to process. Can be any iterable (list, tuple,
                 generator, etc.).
        reducer: Transducer that defines how to collect/accumulate results.
                Defaults to appending() which collects into a list.
        init: Initial accumulator value. If not provided, uses the reducer's
             initial() method to get the starting value.
    
    Returns:
        Final accumulated result after processing all items and calling
        the reducer's complete() method.
    
    Raises:
        TypeError: If transducer or reducer don't implement required protocol
        Exception: Any exception raised by the transducer, reducer, or iterable
    
    Examples:
        Basic usage with default list collection:
        >>> from sumps.transducer import transduce, mapping
        >>> result = transduce(mapping(lambda x: x * 2), [1, 2, 3])
        >>> result  # [2, 4, 6]
        
        Composed transformations:
        >>> from sumps.transducer import mapping, filtering, take
        >>> pipeline = mapping(lambda x: x * 2) | filtering(lambda x: x > 5) | take(2)
        >>> result = transduce(pipeline, [1, 2, 3, 4, 5, 6])
        >>> result  # [6, 8]
        
        Custom reducer and initial value:
        >>> from sumps.transducer import conjoining
        >>> result = transduce(mapping(str.upper), ['a', 'b'], conjoining())
        >>> result  # ('A', 'B')
        
        With custom initial value:
        >>> result = transduce(mapping(lambda x: x), [1, 2, 3], appending(), [0])
        >>> result  # [0, 1, 2, 3]
    
    Performance Notes:
        - Single-pass processing: No intermediate collections created
        - Early termination: Processing stops when Reduced wrapper is encountered
        - Memory efficient: Only the final accumulator is kept in memory
        - Lazy evaluation: Works with generators and infinite iterables
    """
    # Validate inputs
    if not callable(transducer):
        raise TypeError("transducer must be callable")
    
    # Use default reducer if none provided
    if reducer is None:
        reducer = cast(Transducer[T, U], appending())
    
    # Apply transducer to create the processing pipeline
    try:
        pipeline = transducer(reducer)
    except Exception as e:
        raise TypeError(f"Failed to apply transducer to reducer: {e}") from e
    
    # Initialize accumulator
    if init is _UNSET:
        try:
            accumulator = pipeline.initial()
        except Exception as e:
            raise RuntimeError(f"Failed to initialize accumulator: {e}") from e
    else:
        accumulator = init
    
    # Process items with context manager support
    try:
        # Use context manager if available
        if hasattr(pipeline, '__enter__'):
            with pipeline:
                accumulator = _process_items(pipeline, iterable, accumulator)
        else:
            accumulator = _process_items(pipeline, iterable, accumulator)
        
        # Complete the reduction
        return pipeline.complete(accumulator)
        
    except Exception as e:
        # Ensure cleanup happens even on error
        if hasattr(pipeline, '__exit__'):
            try:
                pipeline.__exit__(type(e), e, e.__traceback__)
            except Exception:
                pass  # Don't mask original exception
        raise


def _process_items(pipeline: Transducer, iterable: Iterable[Any], accumulator: Any) -> Any:
    """Process items through the pipeline with early termination support.
    
    Args:
        pipeline: Configured transducer pipeline
        iterable: Items to process
        accumulator: Current accumulator value
        
    Returns:
        Final accumulator after processing all items or early termination
    """
    try:
        for item in iterable:
            accumulator = pipeline.step(accumulator, item)
            
            # Check for early termination
            if isinstance(accumulator, Reduced):
                return accumulator.value
                
    except Exception as e:
        raise RuntimeError(f"Error processing item: {e}") from e
    
    return accumulator


async def atransduce(
    transducer: Callable[[AsyncTransducer[T, U]], AsyncTransducer[T, Any]],
    iterable: AsyncIterable[Any],
    reducer: AsyncTransducer[T, U] | None = None,
    init: T = _UNSET,
) -> T:
    """Execute an async transduction pipeline on an async iterable.
    
    Async version of transduce() that works with AsyncTransducer protocol
    and async iterables. Provides the same composable, memory-efficient
    processing for async data streams.
    
    Args:
        transducer: Function that transforms an async reducer into a new async reducer
        iterable: Async input data to process (AsyncIterable)
        reducer: AsyncTransducer that defines how to collect/accumulate results
        init: Initial accumulator value
    
    Returns:
        Final accumulated result after processing all items
    
    Example:
        >>> async def process_stream():
        ...     result = await atransduce(
        ...         async_mapping(lambda x: x * 2),
        ...         async_range(5),
        ...         async_appending()
        ...     )
        ...     return result  # [0, 2, 4, 6, 8]
    """
    # Validate inputs
    if not callable(transducer):
        raise TypeError("transducer must be callable")
    
    # Use default reducer if none provided
    if reducer is None:
        from .operator.appending import aappending
        reducer = cast(AsyncTransducer[T, U], aappending())
    
    # Apply transducer to create the processing pipeline
    try:
        pipeline = transducer(reducer)
    except Exception as e:
        raise TypeError(f"Failed to apply async transducer to reducer: {e}") from e
    
    # Initialize accumulator
    if init is _UNSET:
        try:
            accumulator = await pipeline.initial()
        except Exception as e:
            raise RuntimeError(f"Failed to initialize async accumulator: {e}") from e
    else:
        accumulator = init
    
    # Process items with async context manager support
    try:
        # Use async context manager if available
        if hasattr(pipeline, '__aenter__'):
            async with pipeline:
                accumulator = await _aprocess_items(pipeline, iterable, accumulator)
        else:
            accumulator = await _aprocess_items(pipeline, iterable, accumulator)
        
        # Complete the reduction
        return await pipeline.complete(accumulator)
        
    except Exception as e:
        # Ensure cleanup happens even on error
        if hasattr(pipeline, '__aexit__'):
            try:
                await pipeline.__aexit__(type(e), e, e.__traceback__)
            except Exception:
                pass  # Don't mask original exception
        raise


async def _aprocess_items(pipeline: AsyncTransducer, iterable: AsyncIterable[Any], accumulator: Any) -> Any:
    """Process items through the async pipeline with early termination support.
    
    Args:
        pipeline: Configured async transducer pipeline
        iterable: Async items to process
        accumulator: Current accumulator value
        
    Returns:
        Final accumulator after processing all items or early termination
    """
    try:
        async for item in iterable:
            accumulator = await pipeline.step(accumulator, item)
            
            # Check for early termination
            if isinstance(accumulator, Reduced):
                return accumulator.value
                
    except Exception as e:
        raise RuntimeError(f"Error processing async item: {e}") from e
    
    return accumulator
