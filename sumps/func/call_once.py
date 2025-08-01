import threading
from functools import wraps

import curio

from sumps.aio import iscoroutinefunction

__all__ = ["call_once"]


def call_once(func):
    """Decorator that ensures a function is called only once, caching the result.

    Supports both synchronous and asynchronous functions with thread-safe execution.
    """
    # Cache for storing the function result
    result = None
    # Flag to track if function has been called
    called = False

    # Handle synchronous functions
    if not iscoroutinefunction(func):
        # Use threading lock for synchronous functions
        lock = threading.Lock()

        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal called, result
            # First check without lock for performance
            if not called:
                # Acquire lock for thread safety
                with lock:
                    # Double-checked locking pattern
                    if not called:
                        # Call function and cache result
                        result = func(*args, **kwargs)
                        called = True
            # Return cached result
            return result

        return wrapper

    # Use curio lock for asynchronous functions
    lock = curio.Lock()

    @wraps(func)
    async def awrapper(*args, **kwargs):
        nonlocal called, result
        # First check without lock for performance
        if not called:
            # Acquire async lock for coroutine safety
            async with lock:
                # Double-checked locking pattern
                if not called:
                    # Await function call and cache result
                    result = await func(*args, **kwargs)
                    called = True
        # Return cached result
        return result

    return awrapper
