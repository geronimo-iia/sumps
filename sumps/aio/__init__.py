"""AIO defines curio extention."""

from .asyncio_support import asyncio_context, run_in_asyncio
from .kernel import Kernel
from .queue import QueueIterator, UniversalQueueIterator, iter
from .run_in import run_in_process, run_in_thread
from .signals import TERMINATION_SIGNALS, SignalEvent, SignalHandler
from .wrapper import ensure_async, iscoroutinefunction

__all__ = [
    "asyncio_context",
    "run_in_asyncio",
    # kernel
    "Kernel",
    # queue
    "iter",
    "UniversalQueueIterator",
    "QueueIterator",
    #run_in
    "run_in_process",
    "run_in_thread",
    # wrapper
    "ensure_async",
    "iscoroutinefunction",
    # signals
    "SignalEvent",
    "SignalHandler",
    "TERMINATION_SIGNALS",
]
