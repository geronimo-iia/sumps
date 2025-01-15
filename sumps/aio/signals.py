"""Signal handling.

Listen a group of signal:

```
    async def my_handler(signal_number):
        print(f"receive {signal_number}")

    task =  await SignalSet.listen(signals=[....], handler=my_handler)
    await task.join()
    print(f"End")
```

In Python, signals can only be caught and processed in the main thread by a signal handler
installed via the signal built-in module.
To communicate a signal to Curio, you can use a UniversalEvent.
see https://curio.readthedocs.io/en/latest/howto.html#how-do-you-catch-signals

Many of these features can be abstracted into classes if you wish.
For example, here is a class (courtesy of Keith Dart):

"""

from __future__ import annotations

import signal
from collections.abc import Awaitable, Callable
from contextlib import suppress

from curio import UniversalEvent, spawn

__all__ = ["SignalEvent", "spawn_signals_listener", "SignalHandler", "TERMINATION_SIGNALS"]

type SignalHandler = Callable[[], Awaitable[None]]

TERMINATION_SIGNALS: list[signal.Signals] = [signal.SIGQUIT, signal.SIGTERM, signal.SIGINT, signal.SIGHUP]


class SignalEvent(UniversalEvent):
    """Define a signal event.

    usage:

    ```python
    sigint_evt = SignalEvent(signal.SIGINT)


    async def main():
        print("Waiting for a signal")
        await sigint_evt.wait()
        print("Got it!")
    ```

    """

    def __init__(self, *signos: signal.Signals):
        super().__init__()
        # keep original handler
        self._old = old = {}
        for signo in signos:
            orig = signal.signal(signo, self._handler)
            old[signo] = orig

    def _handler(self, signo, frame):
        self.set()  # type: ignore

    def __del__(self):
        # restore original signal handler
        with suppress(TypeError):
            while self._old:
                signo, handler = self._old.popitem()
                signal.signal(signo, handler)


async def spawn_signals_listener(handler: SignalHandler, *signos: signal.Signals) -> Callable[[], Awaitable[None]]:
    """Spawn a signal listener task.

    Returns: an async function to cancel it.

    """

    async def _wait_for_signals(sigint_evt: SignalEvent):
        while True:
            await sigint_evt.wait()
            await handler()
            sigint_evt.clear()

    sigint_evt = SignalEvent(*signos)
    task = await spawn(_wait_for_signals, sigint_evt, daemon=True)

    async def _clear():
        nonlocal sigint_evt, task
        del sigint_evt
        await task.cancel()

    return _clear
