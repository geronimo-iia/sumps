from curio.meta import iscoroutinefunction

__all__ = ["async_wrapper"]


def async_wrapper(target):
    """wrap a sync function into an async one."""

    async def wrapped(*args, **kwds):
        return target(*args, **kwds)

    return target if iscoroutinefunction(target) else wrapped
