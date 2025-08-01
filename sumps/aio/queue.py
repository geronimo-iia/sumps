"""Async queue iterators for curio queues.

Provides iterator wrappers around curio Queue types to enable
async iteration patterns with proper task completion handling.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator

from curio import CancelledError, LifoQueue, PriorityQueue, Queue, UniversalQueue
from curio.meta import awaitable

__all__ = ["iter", "QueueIterator", "UniversalQueueIterator"]

type SimpleQueue = Queue | PriorityQueue | LifoQueue

def iter(queue: SimpleQueue | UniversalQueue) -> AsyncIterator:
    """Create an async iterator from a curio queue.
    
    Args:
        queue: A curio queue (Queue, PriorityQueue, LifoQueue, or UniversalQueue)
        
    Returns:
        AsyncIterator that yields items from the queue
    """
    if isinstance(queue, UniversalQueue):
        return UniversalQueueIterator(queue=queue)
    return QueueIterator(queue=queue)


class QueueIterator(AsyncIterator):
    """Async iterator for simple curio queues.
    
    Wraps Queue, PriorityQueue, or LifoQueue to provide async iteration
    with proper task completion handling.
    """

    def __init__(self, queue: SimpleQueue) -> None:
        """Initialize the queue iterator.
        
        Args:
            queue: The curio queue to iterate over
        """
        self._halt = False
        self.queue = queue


    def __aiter__(self) -> QueueIterator:
        """Return self as the async iterator."""
        return self

    
    async def __anext__(self):
        """Get the next item from the queue.
        
        Returns:
            The next item from the queue
            
        Raises:
            StopAsyncIteration: When halted, cancelled, or empty item received
        """
        if self._halt:
            raise StopAsyncIteration()
        try:
            item = await self.queue.get()
            await self.queue.task_done()
            if not item:
                raise StopAsyncIteration()
            return item
        except CancelledError as error:
            raise StopAsyncIteration() from error

    async def halt(self):
        """Stop the iterator on next iteration."""
        self._halt = True


class UniversalQueueIterator(AsyncIterator, Iterator):
    """Dual sync/async iterator for curio UniversalQueue.
    
    Supports both synchronous and asynchronous iteration patterns
    for UniversalQueue with proper task completion handling.
    """

    def __init__(self, queue: UniversalQueue) -> None:
        """Initialize the universal queue iterator.
        
        Args:
            queue: The curio UniversalQueue to iterate over
        """
        self._halt = False
        self.queue = queue

    def __aiter__(self) -> UniversalQueueIterator:
        """Return self as the async iterator."""
        return self

    def __iter__(self) -> UniversalQueueIterator:
        """Return self as the sync iterator."""
        return self

    def __next__(self):
        """Get the next item synchronously.
        
        Returns:
            The next item from the queue
            
        Raises:
            StopIteration: When halted, cancelled, or empty item received
        """
        if self._halt:
            raise StopIteration()

        try:
            item = self.queue.get()
            self.queue.task_done_sync()
            if not item:
                raise StopIteration()
            return item

        except CancelledError as error:
            raise StopIteration() from error

    async def __anext__(self):
        """Get the next item asynchronously.
        
        Returns:
            The next item from the queue
            
        Raises:
            StopAsyncIteration: When halted, cancelled, or empty item received
        """
        if self._halt:
            raise StopAsyncIteration()
        try:
            item = await self.queue.get()
            await self.queue.task_done()
            if not item:
                raise StopAsyncIteration()
            return item
        except CancelledError as error:
            raise StopAsyncIteration() from error

    def halt(self):  # type: ignore
        """Stop the iterator on next iteration (sync version)."""
        self._halt = True

    @awaitable(halt)
    async def halt(self):
        """Stop the iterator on next iteration (async version)."""
        self._halt = True
