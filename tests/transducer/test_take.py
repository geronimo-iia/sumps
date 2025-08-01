"""Tests for take operators."""

import pytest
from sumps.transducer import transduce, atransduce
# Simple identity function for tests
identity = lambda x: x
from sumps.transducer.operator import take, atake, appending, aappending
from sumps.transducer.operator.async_utils import async_from_iterable


class TestTake:
    """Test sync take operator."""
    
    def test_basic_take(self):
        result = transduce(identity, [1, 2, 3, 4, 5], take(3)(appending()))
        assert result == [1, 2, 3]
    
    def test_take_zero(self):
        result = transduce(identity, [1, 2, 3], take(0)(appending()))
        assert result == []


@pytest.mark.curio
class TestAsyncTake:
    """Test async take operator."""
    
    async def test_basic_atake(self):
        result = await atransduce(identity, async_from_iterable([1, 2, 3, 4, 5]), atake(3)(aappending()))
        assert result == [1, 2, 3]
    
    async def test_take_zero(self):
        result = await atransduce(identity, async_from_iterable([1, 2, 3]), atake(0)(aappending()))
        assert result == []