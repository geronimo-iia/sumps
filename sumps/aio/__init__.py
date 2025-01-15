"""AIO defines curio extention."""

from .asyncio_support import asyncio_context, asyncio_spawn
from .kernel import Kernel
from .queue import IterableQueue, IterableUniversalQueue, iter
from .run_in import run_in_process, run_in_thread
from .signals import TERMINATION_SIGNALS, SignalEvent, SignalHandler, spawn_signals_listener
from .wrapper import async_wrapper

__all__ = [
    "asyncio_context",
    "asyncio_spawn",
    "Kernel",
    "iter",
    "IterableQueue",
    "IterableUniversalQueue",
    "run_in_process",
    "run_in_thread",
    "async_wrapper",
    "SignalEvent",
    "SignalHandler",
    "TERMINATION_SIGNALS",
    "spawn_signals_listener",
]
