"""Uses curio Queue as Iterable."""

from __future__ import annotations

from collections.abc import Iterable

from curio import CancelledError, LifoQueue, PriorityQueue, Queue, UniversalQueue
from curio.meta import awaitable

__all__ = ["iter", "IterableQueue", "IterableUniversalQueue"]

type SimpleQueue = Queue | PriorityQueue | LifoQueue


def iter(queue: SimpleQueue | UniversalQueue) -> Iterable:
    if isinstance(queue, UniversalQueue):
        return IterableUniversalQueue(queue=queue)
    return IterableQueue(queue=queue)


class IterableQueue(Iterable):
    """Create an Iterable Queue."""

    def __init__(self, queue: SimpleQueue) -> None:
        self._halt = False
        self.queue = queue

    def __aiter__(self):
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


class IterableUniversalQueue(Iterable):
    """Create an Iterable UniversalQueue."""

    def __init__(self, queue: UniversalQueue) -> None:
        self._halt = False
        self.queue = queue

    def __aiter__(self) -> IterableUniversalQueue:
        return self

    def __iter__(self) -> IterableUniversalQueue:
        return self

    def __next__(self):
        if self._halt:
            raise StopIteration()

        try:
            item = self.queue.get()
            self.queue.task_done_sync()
            if not item:
                raise StopAsyncIteration()
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
