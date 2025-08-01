from math import sqrt

import pytest

from sumps.func import compose
from sumps.transducer import (
    batching,
    conjoining,
    drop,
    drop_last,
    enumerating,
    expecting_single,
    filtering,
    first_true,
    mapping,
    nth,
    repeating,
    take,
    take_last,
    transduce,
)


def is_prime(x):
    if x < 2:
        return False
    return all(x % i != 0 for i in range(2, int(sqrt(x)) + 1))


def square(x):
    return x * x


def test_transduce():
    assert transduce(mapping(str.upper), "Reduce can perform mapping too!".split()) == [
        "REDUCE",
        "CAN",
        "PERFORM",
        "MAPPING",
        "TOO!",
    ]
    assert transduce(filtering(lambda x: x % 2 != 0), [1, 2, 3, 4, 5, 6, 7, 8]) == [1, 3, 5, 7]

    assert transduce(filtering(lambda x: x % 2 != 0), [1, 2, 3, 4, 5, 6, 7, 8], conjoining()) == (1, 3, 5, 7)

    assert transduce(first_true(lambda x: x % 2 != 0), [1, 2, 3, 4, 5, 6, 7, 8]) == [1]

    assert transduce(compose(filtering(is_prime), mapping(square)), range(10)) == [4, 9, 25, 49]

    assert transduce(compose(filtering(is_prime), mapping(square), drop_last(limit=1)), range(10)) == [4, 9, 25]

    assert transduce(compose(filtering(is_prime), mapping(square), take_last(limit=1)), range(10)) == [49]

    assert transduce(compose(filtering(is_prime), mapping(square), nth(n=3)), range(10)) == [25]

    assert transduce(compose(filtering(is_prime), mapping(square), drop(limit=2)), range(10)) == [25, 49]

    assert transduce(compose(filtering(is_prime), mapping(square), take(limit=2)), range(10)) == [4, 9]

    assert transduce(compose(filtering(is_prime), mapping(square), take(limit=2), repeating(num_times=2)), range(10)) == [4, 4, 9, 9]

    assert transduce(compose(filtering(is_prime), mapping(square), enumerating(), nth(n=3)), range(10)) == [(2, 25)]

    assert transduce(compose(filtering(is_prime), mapping(square), enumerating(), batching(size=2)), range(5)) == [[(0, 4), (1, 9)]]


def test_transduce_expecting_single():
    assert transduce(compose(filtering(is_prime), mapping(square), enumerating(), nth(n=3), expecting_single()), range(10)) == [(2, 25)]
    with pytest.raises(RuntimeError):
        transduce(compose(filtering(is_prime), mapping(square), enumerating(), expecting_single()), range(10))
