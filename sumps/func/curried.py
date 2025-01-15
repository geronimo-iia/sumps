from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from inspect import signature
from typing import TypeVar, overload

__all__ = ["curried"]

T1 = TypeVar("T1", contravariant=True)
T2 = TypeVar("T2", contravariant=True)
T3 = TypeVar("T3", contravariant=True)
T4 = TypeVar("T4", contravariant=True)
T5 = TypeVar("T5", contravariant=True)
T6 = TypeVar("T6", contravariant=True)
T7 = TypeVar("T7", contravariant=True)
R = TypeVar("R", covariant=True)


@overload
def curried(f: Callable[[], R]) -> Callable[[], R]:
    raise Exception()


@overload
def curried(f: Callable[[T1], R]) -> Callable[[T1], R]:
    raise Exception()


@overload
def curried(f: Callable[[T1, T2], R]) -> Callable[[T1], Callable[[T2], R]]:
    raise Exception()


@overload
def curried(f: Callable[[T1, T2, T3], R]) -> Callable[[T1], Callable[[T2], Callable[[T3], R]]]:
    raise Exception()


@overload
def curried(f: Callable[[T1, T2, T3, T4], R]) -> Callable[[T1], Callable[[T2], Callable[[T3], Callable[[T4], R]]]]:
    raise Exception()


@overload
def curried(
    f: Callable[[T1, T2, T3, T4, T5], R],
) -> Callable[[T1], Callable[[T2], Callable[[T3], Callable[[T4], Callable[[T5], R]]]]]:
    raise Exception()


@overload
def curried(
    f: Callable[[T1, T2, T3, T4, T5, T6], R],
) -> Callable[[T1], Callable[[T2], Callable[[T3], Callable[[T4], Callable[[T5], Callable[[T6], R]]]]]]:
    raise Exception()


@overload
def curried(
    f: Callable[[T1, T2, T3, T4, T5, T6, T7], R],
) -> Callable[[T1], Callable[[T2], Callable[[T3], Callable[[T4], Callable[[T5], Callable[[T6], Callable[[T7], R]]]]]]]:
    raise Exception()


def curried(func):  # type: ignore
    args_len = len(signature(func).parameters)

    if args_len <= 1:
        return func

    if args_len > 7:
        raise RuntimeError("curried function with more than 7 parameters is not supported")

    @wraps(func)
    def curried_function(*args, **keywords):
        _args = args
        _keywords = keywords

        if len(_args) + len(_keywords) >= args_len:
            return func(*_args, **_keywords)

        def inner(*args, **keywords):
            nonlocal _args, _keywords
            local_args = _args + args
            local_keywords = {**_keywords, **keywords}
            return curried_function(*local_args, **local_keywords)

        return inner

    return curried_function
