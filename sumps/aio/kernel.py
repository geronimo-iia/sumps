"""Defines a kernel."""

from contextlib import ExitStack

from curio import Kernel as _Kernel
from curio import workers

from .asyncio_support import init_asyncio_loop

__all__ = ["Kernel"]


class Kernel(ExitStack):
    """
    Kernel is a context compatible with curio and asyncio.
    """

    def __init__(
        self,
        max_processes: int | None = None,
        max_threads: int | None = None,
        debug: bool = False,
        with_asyncio: bool = True,
    ) -> None:
        super().__init__()
        assert max_processes is None or max_processes > 0
        assert max_threads is None or max_threads > 0

        # configure curio worker
        if max_threads:
            workers.MAX_WORKER_THREADS = max_threads
        if max_processes:
            workers.MAX_WORKER_PROCESSES = max_processes

        # associate curio kernel
        self._kernel = self.enter_context(_Kernel(debug=debug))

        # add asyncio support
        if with_asyncio:
            self.callback(init_asyncio_loop())

    @property
    def max_threads(self) -> int:
        return workers.MAX_WORKER_THREADS

    @property
    def max_processes(self) -> int:
        return workers.MAX_WORKER_PROCESSES

    def run(self, corofunc=None, *args, shutdown=False):
        """Submit a new task to the kernel."""
        return self._kernel.run(*args, corofunc=corofunc, shutdown=shutdown)
