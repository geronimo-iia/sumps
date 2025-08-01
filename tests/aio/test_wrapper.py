from functools import partial

import pytest

from sumps.aio.wrapper import ensure_async, iscoroutinefunction


# Test fixtures
async def async_func():
    return "async"

def sync_func():
    return "sync"

async def async_gen():
    yield "async_gen"

class AsyncCallable:
    async def __call__(self):
        return "async_callable"

class SyncCallable:
    def __call__(self):
        return "sync_callable"

class AwaitableClass:
    def __await__(self):
        return iter([])

class AwaitableAttrClass:
    _awaitable = True

class BoundMethodClass:
    async def async_method(self):
        return "async_method"
    
    def sync_method(self):
        return "sync_method"


class TestIscoroutineFunction:
    def test_standard_async_function(self):
        assert iscoroutinefunction(async_func) is True
    
    def test_standard_sync_function(self):
        assert iscoroutinefunction(sync_func) is False
    
    def test_partial_async_function(self):
        partial_async = partial(async_func)
        assert iscoroutinefunction(partial_async) is True
    
    def test_partial_sync_function(self):
        partial_sync = partial(sync_func)
        assert iscoroutinefunction(partial_sync) is False
    
    def test_bound_async_method(self):
        obj = BoundMethodClass()
        assert iscoroutinefunction(obj.async_method) is True
    
    def test_bound_sync_method(self):
        obj = BoundMethodClass()
        assert iscoroutinefunction(obj.sync_method) is False
    
    def test_coroutine_object(self):
        coro = async_func()
        assert iscoroutinefunction(coro) is True
        coro.close()
    
    def test_async_callable_object(self):
        async_callable = AsyncCallable()
        assert iscoroutinefunction(async_callable) is True
    
    def test_sync_callable_object(self):
        sync_callable = SyncCallable()
        assert iscoroutinefunction(sync_callable) is False
    
    def test_awaitable_object(self):
        awaitable = AwaitableClass()
        assert iscoroutinefunction(awaitable) is True
    
    def test_awaitable_attr_object(self):
        awaitable_attr = AwaitableAttrClass()
        assert iscoroutinefunction(awaitable_attr) is True
    
    def test_async_generator(self):
        assert iscoroutinefunction(async_gen) is True
    
    def test_none_object(self):
        assert iscoroutinefunction(None) is False
    
    def test_string_object(self):
        assert iscoroutinefunction("string") is False


class TestEnsureAsync:
    def test_async_function_unchanged(self):
        result = ensure_async(async_func)
        assert result is async_func
    
    def test_sync_function_wrapped(self):
        result = ensure_async(sync_func)
        assert result is not sync_func
        assert iscoroutinefunction(result) is True
    
    @pytest.mark.curio
    async def test_wrapped_sync_function_execution(self):
        wrapped = ensure_async(sync_func)
        result = await wrapped()
        assert result == "sync"
    
    @pytest.mark.curio
    async def test_wrapped_sync_function_with_args(self):
        def sync_with_args(x, y=10):
            return x + y
        
        wrapped = ensure_async(sync_with_args)
        result = await wrapped(5, y=15)
        assert result == 20
    
    def test_partial_async_function_unchanged(self):
        partial_async = partial(async_func)
        result = ensure_async(partial_async)
        assert result is partial_async
    
    def test_partial_sync_function_wrapped(self):
        partial_sync = partial(sync_func)
        result = ensure_async(partial_sync)
        assert result is not partial_sync
        assert iscoroutinefunction(result) is True
    
    def test_bound_async_method_unchanged(self):
        obj = BoundMethodClass()
        method = obj.async_method
        result = ensure_async(method)
        assert result is method
    
    def test_bound_sync_method_wrapped(self):
        obj = BoundMethodClass()
        method = obj.sync_method
        result = ensure_async(method)
        assert result is not method
        assert iscoroutinefunction(result) is True
    
    def test_async_callable_unchanged(self):
        async_callable = AsyncCallable()
        result = ensure_async(async_callable)
        assert result is async_callable
    
    def test_sync_callable_wrapped(self):
        sync_callable = SyncCallable()
        result = ensure_async(sync_callable)
        assert result is not sync_callable
        assert iscoroutinefunction(result) is True
    
    def test_coroutine_object_raises_error(self):
        coro = async_func()
        with pytest.raises(TypeError, match="Cannot wrap coroutine object"):
            ensure_async(coro)
        coro.close()
    
    def test_wrapped_function_preserves_metadata(self):
        def documented_func():
            """A documented function"""
            return "result"
        
        wrapped = ensure_async(documented_func)
        assert wrapped.__name__ == documented_func.__name__
        assert wrapped.__doc__ == documented_func.__doc__