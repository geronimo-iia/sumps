"""
Synchronous Functions:

    Basic single call behavior
    Function with arguments (only first call args used)
    Thread safety with concurrent execution
    Metadata preservation

Asynchronous Functions:

    Basic single call behavior for async functions
    Async function with arguments
    Concurrency safety with multiple awaits
    Async metadata preservation

Key Test Scenarios:

    Verifies function is called exactly once
    Tests caching of results
    Validates thread/concurrency safety
    Ensures function metadata is preserved via @wraps
    Tests both sync and async code paths
"""

import threading
import time

import curio
import pytest

from sumps.func.call_once import call_once


def test_sync_function_called_once():
    """Test that synchronous function is called only once."""
    call_count = 0
    first_call_args = None
    
    @call_once
    def sync_func(a, b, **kwargs):
        nonlocal call_count, first_call_args
        if call_count == 0:
            first_call_args = ((a, b), kwargs)
        call_count += 1
        return 42


    result1 = sync_func(1, 2, key="value")
    result2 = sync_func(3, 4, other="data")

    assert result1 == 42
    assert result2 == 42
    assert call_count == 1
    assert first_call_args == ((1, 2), {"key": "value"})



def test_sync_function_thread_safety():
    """Test thread safety of synchronous function."""
    call_count = 0

    @call_once
    def slow_func():
        nonlocal call_count
        time.sleep(0.1)
        call_count += 1
        return call_count

    results = []

    def worker():
        results.append(slow_func())

    threads = [threading.Thread(target=worker) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert all(r == 1 for r in results)
    assert call_count == 1


@pytest.mark.curio
async def test_async_function_called_once():
    """Test that asynchronous function is called only once."""
    call_count = 0

    @call_once
    async def async_func():
        nonlocal call_count
        call_count += 1
        return "async_result"


    result1 = await async_func()
    result2 = await async_func()

    assert result1 == "async_result"
    assert result2 == "async_result"
    assert call_count == 1


@pytest.mark.curio
async def test_async_function_with_args():
    """Test asynchronous function with arguments."""
    call_count = 0

    @call_once
    async def async_func(a, b, key=None):
        nonlocal call_count
        call_count += 1
        return f"{a}-{b}-{key}"

    result1 = await async_func(1, 2, key="test")
    result2 = await async_func(3, 4, key="other")

    assert result1 == "1-2-test"
    assert result2 == "1-2-test"
    assert call_count == 1


@pytest.mark.curio
async def test_async_function_concurrency():
    """Test concurrent execution of async function."""
    call_count = 0

    @call_once
    async def slow_async_func():
        nonlocal call_count
        await curio.sleep(0.1)
        call_count += 1
        return call_count

    async with curio.TaskGroup() as group:
        tasks = [await group.spawn(slow_async_func) for _ in range(5)]
    
    results = [task.result for task in tasks]

    assert all(r == 1 for r in results)
    assert call_count == 1


def test_function_metadata_preserved():
    """Test that function metadata is preserved."""

    @call_once
    def original_func():
        """Original docstring."""
        return "value"


    assert original_func.__name__ == "original_func"
    assert original_func.__doc__ == "Original docstring."


@pytest.mark.curio
async def test_async_function_metadata_preserved():
    """Test that async function metadata is preserved."""

    @call_once
    async def original_async():
        """Async docstring."""
        return "async_value"


    assert original_async.__name__ == "original_async"
    assert original_async.__doc__ == "Async docstring."
