import threading
import time

import curio
import pytest

from sumps.func.call_once import call_once


class TestCallOnceSync:
    def test_function_called_once(self):
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

    def test_thread_safety(self):
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

    def test_metadata_preserved(self):
        """Test that function metadata is preserved."""
        @call_once
        def original_func():
            """Original docstring."""
            return "value"

        assert original_func.__name__ == "original_func"
        assert original_func.__doc__ == "Original docstring."


class TestCallOnceAsync:
    @pytest.mark.curio
    async def test_function_called_once(self):
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
    async def test_function_with_args(self):
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
    async def test_concurrency(self):
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

    @pytest.mark.curio
    async def test_metadata_preserved(self):
        """Test that async function metadata is preserved."""
        @call_once
        async def original_async():
            """Async docstring."""
            return "async_value"

        assert original_async.__name__ == "original_async"
        assert original_async.__doc__ == "Async docstring."
