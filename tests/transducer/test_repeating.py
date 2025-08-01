"""Tests for repeating operators."""

import pytest
from sumps.transducer import transduce, atransduce
# Simple identity function for tests
identity = lambda x: x
from sumps.transducer.operator import repeating, arepeating, appending, aappending
from sumps.transducer.operator.async_utils import async_from_iterable


class TestRepeating:
    """Test sync repeating operator."""
    
    def test_basic_repeating(self):
        result = transduce(identity, [1, 2], repeating(3)(appending()))
        assert result == [1, 1, 1, 2, 2, 2]
    
    def test_repeat_zero(self):
        result = transduce(identity, [1, 2], repeating(0)(appending()))
        assert result == []


@pytest.mark.curio
class TestAsyncRepeating:
    """Test async repeating operator."""
    
    async def test_basic_arepeating(self):
        result = await atransduce(identity, async_from_iterable([1, 2]), arepeating(3)(aappending()))
        assert result == [1, 1, 1, 2, 2, 2]
    
    async def test_repeat_zero(self):
        result = await atransduce(identity, async_from_iterable([1, 2]), arepeating(0)(aappending()))
        assert result == []