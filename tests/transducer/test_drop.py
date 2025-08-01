"""Tests for drop operators."""

import pytest
from sumps.transducer import transduce, atransduce
# Simple identity function for tests
identity = lambda x: x
from sumps.transducer.operator import drop, adrop, appending, aappending
from sumps.transducer.operator.async_utils import async_from_iterable


class TestDrop:
    """Test sync drop operator."""
    
    def test_basic_drop(self):
        result = transduce(identity, [1, 2, 3, 4, 5], drop(2)(appending()))
        assert result == [3, 4, 5]
    
    def test_drop_zero(self):
        result = transduce(identity, [1, 2, 3], drop(0)(appending()))
        assert result == [1, 2, 3]


@pytest.mark.curio
class TestAsyncDrop:
    """Test async drop operator."""
    
    async def test_basic_adrop(self):
        result = await atransduce(identity, async_from_iterable([1, 2, 3, 4, 5]), adrop(2)(aappending()))
        assert result == [3, 4, 5]
    
    async def test_drop_zero(self):
        result = await atransduce(identity, async_from_iterable([1, 2, 3]), adrop(0)(aappending()))
        assert result == [1, 2, 3]