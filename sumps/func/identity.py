from curio.meta import awaitable

__all__ = ["identity"]


def identity(x):  # type: ignore
    """Identity function. Return x

    >>> identity(3)
    3
    """
    return x


@awaitable(identity)
async def identity(x):
    """Identity function. Return x

    >>> await identity(3)
    3
    """
    return x
