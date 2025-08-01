__all__ = ["identity"]


def identity(x):
    """Identity function. Return x

    Works in both sync and async contexts by simply returning the input unchanged.
    
    >>> identity(3)
    3
    >>> import asyncio
    >>> asyncio.run(identity(3))  # Works in async context too
    3
    """
    return x
