import asyncio
import os
import threading

import curio

from sumps.aio import Kernel, asyncio_context


async def run_in_curio():
    for i in range(10):
        print(f"curio: {i}")
        await curio.sleep(0.1)
    print(f"curio: {os.getpid()}:{threading.current_thread().native_id}")
    return os.getpid(), threading.current_thread().native_id


@asyncio_context
async def run_in_asyncio(start: int, end: int):
    for i in range(start, end):
        print(f"asyncio: {i}")
        await asyncio.sleep(0.1)
    print(f"asyncio: {os.getpid()}:{threading.current_thread().native_id}")
    return os.getpid(), threading.current_thread().native_id


async def call_them_all():
    print("Hello from curio")

    async with curio.TaskGroup() as g:
        await g.spawn(run_in_curio)
        await g.spawn(run_in_asyncio, 100, 110)
    assert g.results
    assert g.results[0] != g.results[1]
    a, b = g.results[0]
    c, d = g.results[1]
    assert a == c
    assert b != d


def test_call_them_all():
    with Kernel() as k:
        k.run(call_them_all, shutdown=True)
