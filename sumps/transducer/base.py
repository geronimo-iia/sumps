"""Transducer model definitions for composable data transformations.

Provides protocols for sync/async transducers with type safety and resource management.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable, Awaitable, Sized
from typing import Any, Protocol, TypeVar, runtime_checkable
from types import TracebackType

T = TypeVar('T')

@runtime_checkable
class SizedResult[T](Sized, Protocol):
    """Protocol for results that support len() and slicing."""
    def __getitem__(self, key) -> T: ...


__all__ = [
    "Predicate",
    "Transform",
    "Transducer",
    "AsyncTransducer",
    "BaseTransducer",
    "BaseAsyncTransducer",
    "SizedResult",
    "Reduced",
    "is_reducer",
]

Result = TypeVar("Result")
Input = TypeVar("Input")

type Reducing[Result, Input] = Callable[[Result, Input], Result]

type Predicate[Input] = Callable[[Input], bool]

type Transform[Input, Result] = Callable[[Input], Result]


@runtime_checkable
class Transducer[Result, Input](Protocol):
    """Protocol for composable data transformations with resource management."""
    
    def initial(self) -> Result:
        """Return the initial seed value for the reduction."""
        ...

    def step(self, result: Result, item: Input) -> Result:
        """Process the next item in the reduction."""
        ...

    def complete(self, result: Result) -> Result:
        """Finalize the result and perform cleanup."""
        ...
    
    def __enter__(self) -> Transducer[Result, Input]:
        """Enter context manager for resource setup."""
        ...
    
    def __exit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None) -> None:
        """Exit context manager for resource cleanup."""
        ...


@runtime_checkable
class AsyncTransducer[Result, Input](Protocol):
    """Async protocol for composable data transformations with resource management."""
    
    async def initial(self) -> Result:
        """Return the initial seed value for the reduction."""
        ...

    async def step(self, result: Result, item: Input) -> Result:
        """Process the next item in the reduction asynchronously."""
        ...

    async def complete(self, result: Result) -> Result:
        """Finalize the result and perform cleanup asynchronously."""
        ...
    
    async def __aenter__(self) -> AsyncTransducer[Result, Input]:
        """Enter async context manager for resource setup."""
        ...
    
    async def __aexit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None) -> None:
        """Exit async context manager for resource cleanup."""
        ...


class BaseTransducer[Result, Input](ABC):
    """Abstract base class with default context manager implementation."""
    
    @abstractmethod
    def initial(self) -> Result:
        """Return the initial seed value for the reduction."""
        ...

    @abstractmethod
    def step(self, result: Result, item: Input) -> Result:
        """Process the next item in the reduction."""
        ...

    @abstractmethod
    def complete(self, result: Result) -> Result:
        """Finalize the result and perform cleanup."""
        ...
    
    def __enter__(self) -> BaseTransducer[Result, Input]:
        """Default context manager entry."""
        return self
    
    def __exit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None) -> None:
        """Default context manager exit (no-op)."""
        pass


class BaseAsyncTransducer[Result, Input](ABC):
    """Abstract async base class with default context manager implementation."""
    
    @abstractmethod
    async def initial(self) -> Result:
        """Return the initial seed value for the reduction."""
        ...

    @abstractmethod
    async def step(self, result: Result, item: Input) -> Result:
        """Process the next item in the reduction asynchronously."""
        ...

    @abstractmethod
    async def complete(self, result: Result) -> Result:
        """Finalize the result and perform cleanup asynchronously."""
        ...
    
    async def __aenter__(self) -> BaseAsyncTransducer[Result, Input]:
        """Default async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None) -> None:
        """Default async context manager exit (no-op)."""
        pass


def is_reducer(obj: Any) -> bool:
    """Check if object implements transducer protocol."""
    return isinstance(obj, (Transducer, AsyncTransducer, BaseTransducer, BaseAsyncTransducer))


class Reduced[T]:
    """A sentinel 'box' used to return the final value of a reduction."""
    __slots__ = ('_value',)

    def __init__(self, value: T) -> None:
        """Initialize with the final reduction value."""
        self._value = value

    @property
    def value(self) -> T:
        """Get the wrapped reduction value."""
        return self._value
    
    def __repr__(self) -> str:
        """String representation of the reduced value."""
        return f"Reduced({self._value!r})"