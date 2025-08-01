"""Defines a kernel supporting curio and asyncio."""

from contextlib import ExitStack

from curio import Kernel as CurioKernel
from curio import workers

from .asyncio_support import AsyncioKernel

__all__ = ["Kernel"]


class Kernel(ExitStack):
    """
    Kernel is a context compatible with curio and asyncio.
    """

    _curio_kernel: CurioKernel
    _asyncio_kernel: AsyncioKernel | None
    _max_asyncio_workers : int

    def __init__(
        self,
        max_processes: int | None = None,
        max_threads: int | None = None,
        debug: bool = False,
        with_asyncio: bool = True,
        max_asyncio_workers: int | None = None,
        asyncio_termination_timeout: int | None = None
    ) -> None:
        super().__init__()
        assert max_processes is None or max_processes > 0
        assert max_threads is None or max_threads > 0
        assert max_asyncio_workers is None or max_asyncio_workers > 0
        assert asyncio_termination_timeout is None or asyncio_termination_timeout > 0

        # configure curio worker
        if max_threads:
            workers.MAX_WORKER_THREADS = max_threads
        if max_processes:
            workers.MAX_WORKER_PROCESSES = max_processes

        # associate curio kernel
        self._curio_kernel = self.enter_context(CurioKernel(debug=debug))

        # associate asyncio kernel
        if with_asyncio:
            self._max_asyncio_workers = max_asyncio_workers if max_asyncio_workers else workers.MAX_WORKER_THREADS
            self._asyncio_kernel = self.enter_context(AsyncioKernel(
                max_workers=self._max_asyncio_workers,
                termination_timeout=asyncio_termination_timeout if asyncio_termination_timeout else 30
            ))
        else:
            self._max_asyncio_workers = 0
            self._asyncio_kernel = None

    @property
    def max_threads(self) -> int:
        return workers.MAX_WORKER_THREADS

    @property
    def max_processes(self) -> int:
        return workers.MAX_WORKER_PROCESSES
    
    @property
    def max_asyncio_workers(self) -> int:
        return self._max_asyncio_workers

    def run(self, corofunc=None, *args, shutdown=False):
        """Submit a new task to the kernel."""
        return self._curio_kernel.run(*args, corofunc=corofunc, shutdown=shutdown)
