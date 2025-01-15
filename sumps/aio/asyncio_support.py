import asyncio
import threading
from concurrent.futures import Future

import curio

__all__ = ["init_asyncio_loop", "asyncio_context", "asyncio_spawn"]


def init_asyncio_loop():
    """Boostrap asyncio loop on a dedicated thread."""

    def _asyncio_worker_thread(loop):
        def _suspended():
            asyncio.set_event_loop(loop)
            loop.run_forever()

        return _suspended

    def _asyncio_thread_terminate(loop, asyncio_thread):
        def _terminate():
            loop.call_soon_threadsafe(loop.stop)
            asyncio_thread.join(timeout=30)

        return _terminate

    _asyncio_loop = asyncio.new_event_loop()

    # define loop in curio/main thread
    asyncio.set_event_loop(_asyncio_loop)

    # Boot the asyncio worker thread
    _worker_thread = threading.Thread(target=_asyncio_worker_thread(_asyncio_loop), name="asyncio-worker")
    _worker_thread.start()

    return _asyncio_thread_terminate(_asyncio_loop, _worker_thread)


def asyncio_context(callable):
    """Run the target async callable in asyncio context."""

    async def run_it(*args):
        _asyncio_loop = asyncio.get_event_loop()
        if not _asyncio_loop:
            raise RuntimeError("Asyncio is not enabled")

        e = curio.UniversalEvent()

        async def _callable():
            # run in asyncio worker thread
            result = await callable(*args)
            await e.set()
            return result

        future = asyncio.run_coroutine_threadsafe(_callable(), _asyncio_loop)
        await e.wait()
        return future.result()

    return run_it


async def asyncio_spawn(callable) -> Future:
    """Spawn a task in asyncio context."""
    _asyncio_loop = asyncio.get_event_loop()
    if not _asyncio_loop:
        raise RuntimeError("Asyncio is not enabled")

    return asyncio.run_coroutine_threadsafe(callable, _asyncio_loop)
