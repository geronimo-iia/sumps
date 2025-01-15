"""Run dedicated function with initial context."""

import contextvars
import functools

from curio import run_in_process as _run_in_process
from curio import run_in_thread as _run_in_thread

__all__ = ["run_in_thread", "run_in_process"]


async def run_in_thread(callable, *args, call_on_cancel=None):
    """
    Run callable(*args) in a separate thread and return the result. If
    cancelled, be aware that the requested callable may or may not have
    executed.  If it start running, it will run fully to completion
    as a kind of zombie.
    """
    return _run_in_thread(_run_in_(callable, *args), call_on_cancel=call_on_cancel)


async def run_in_process(callable, *args):
    """
    Run callable(*args) in a separate process and return the
    result.  In the event of cancellation, the worker process is
    immediately terminated.

    The worker process is created using multiprocessing.Process().
    Communication with the process uses multiprocessing.Pipe() and an
    asynchronous message passing channel.  All function arguments and
    return values are seralized using the pickle module.  When
    cancelled, the Process.terminate() method is used to kill the
    worker process.  This results in a SIGTERM signal being sent to
    the process.

    The handle_cancellation flag, if True, indicates that you intend
    to manage the worker cancellation yourself.  This an advanced
    option.  Any resulting CancelledError has 'task' and 'worker'
    attributes.  task is a background task that's supervising the
    still executing work.  worker is the associated process.

    The worker process is a separate isolated Python interpreter.
    Nothing should be assumed about its global state including shared
    variables, files, or connections.
    """
    return _run_in_process(_run_in_(callable, *args))


def _run_in_(callable, args=()):
    ctx = contextvars.copy_context()
    func_call = functools.partial(ctx.run, callable, *args)
    return func_call
