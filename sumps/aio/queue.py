"""Uses curio Queue as Iterable."""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator

from curio import CancelledError, LifoQueue, PriorityQueue, Queue, UniversalQueue
from curio.meta import awaitable

__all__ = ["iter", "QueueIterator", "UniversalQueueIterator"]

type SimpleQueue = Queue | PriorityQueue | LifoQueue

def iter(queue: SimpleQueue | UniversalQueue) -> AsyncIterator:
    """Returns an AsyncIterator from a curio queue."""
    if isinstance(queue, UniversalQueue):
        return UniversalQueueIterator(queue=queue)
    return QueueIterator(queue=queue)


class QueueIterator(AsyncIterator):
    """Create an Iterable Queue."""

    def __init__(self, queue: SimpleQueue) -> None:
        self._halt = False
        self.queue = queue


    def __aiter__(self) -> QueueIterator:
        return self

    
    async def __anext__(self):
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
        # halt the next iteration
        self._halt = True


class UniversalQueueIterator(AsyncIterator, Iterator):
    """Create an Iterator/AsyncIterator from a curio UniversalQueue."""

    def __init__(self, queue: UniversalQueue) -> None:
        self._halt = False
        self.queue = queue

    def __aiter__(self) -> UniversalQueueIterator:
        return self

    def __iter__(self) -> UniversalQueueIterator:
        return self

    def __next__(self):
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
        # halt the next iteration
        self._halt = True

    @awaitable(halt)
    async def halt(self):
        # halt the next iteration
        self._halt = True
