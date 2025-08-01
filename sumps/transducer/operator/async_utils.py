"""Async utilities for testing and examples."""

from __future__ import annotations
from collections.abc import AsyncIterable
import asyncio

__all__ = ["async_range", "async_from_iterable"]


# Determine which async library to use at module level
try:
    import curio
    _ASYNC_LIB = 'curio'
except ImportError:
    _ASYNC_LIB = 'asyncio'


async def _async_sleep():
    """Sleep function that works with both asyncio and curio."""
    if _ASYNC_LIB == 'curio':
        await curio.sleep(0)
    else:
        await asyncio.sleep(0)

class AsyncRange:
    """Async version of range() for testing async transducers."""
    
    def __init__(self, *args):
        self._range = range(*args)
    
    def __aiter__(self):
        return self
    
    async def __anext__(self):
        try:
            value = next(iter(self._range))
            self._range = range(value + 1, self._range.stop, self._range.step)
            await _async_sleep()  # Yield control
            return value
        except StopIteration:
            raise StopAsyncIteration


def async_range(*args) -> AsyncIterable[int]:
    """Create an async range iterator."""
    return AsyncRange(*args)


class AsyncFromIterable:
    """Convert a regular iterable to async iterable."""
    
    def __init__(self, iterable):
        self._iterable = iterable
    
    def __aiter__(self):
        return self
    
    async def __anext__(self):
        try:
            value = next(iter(self._iterable))
            # Remove the yielded item from iterable
            if hasattr(self._iterable, '__iter__'):
                self._iterable = list(self._iterable)[1:]
            await _async_sleep()  # Yield control
            return value
        except (StopIteration, IndexError):
            raise StopAsyncIteration


def async_from_iterable(iterable) -> AsyncIterable:
    """Convert a regular iterable to async iterable."""
    return AsyncFromIterable(iterable)