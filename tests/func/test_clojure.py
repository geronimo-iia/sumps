import warnings

from sumps.aio import Kernel, iscoroutinefunction
from sumps.func import closure


class TestClosure:
    def test_async(self):
        @closure
        async def adder(a: int, b: int):
            return a + b

        async def closure_async_test():
            f = await adder(a=1, b=2)
            assert f
            assert iscoroutinefunction(f)
            assert await f() == 3
        
        warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*coroutine.*was never awaited")
        
        with Kernel() as k:
            k.run(closure_async_test, shutdown=True)

    def test_sync(self):
        @closure
        def multiplier(a: int, b: int):
            return a * b
            
        f = multiplier(a=1, b=2)
        assert f
        assert not iscoroutinefunction(f)
        assert f() == 2
