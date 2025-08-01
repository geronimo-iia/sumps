import warnings

from sumps.aio import Kernel, iscoroutinefunction
from sumps.func import closure


@closure
async def adder(a: int, b: int):
    return a + b


@closure
def multiplier(a: int, b: int):
    return a * b

async def closure_async_test():
    f = await adder(a=1, b=2)
    assert f
    assert iscoroutinefunction(f)
    assert await f() == 3


def test_closure_async():
    
    # Suppress asyncio cleanup warnings
    warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*coroutine.*was never awaited")
    
    with Kernel() as k:
        k.run(closure_async_test, shutdown=True)

def test_closure_sync():
    f = multiplier(a=1, b=2)
    assert f
    assert not iscoroutinefunction(f)
    assert f() == 2
