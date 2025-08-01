"""Tests for filtering operators."""

import pytest
from sumps.transducer import transduce, atransduce
# Simple identity function for tests
identity = lambda x: x
from sumps.transducer.operator import filtering, afiltering, appending, aappending
from sumps.transducer.operator.async_utils import async_from_iterable


class TestFiltering:
    """Test sync filtering operator."""
    
    def test_basic_filtering(self):
        result = transduce(identity, [1, 2, 3, 4, 5], filtering(lambda x: x % 2 == 0)(appending()))
        assert result == [2, 4]
    
    def test_filter_none(self):
        result = transduce(identity, [1, 3, 5], filtering(lambda x: x % 2 == 0)(appending()))
        assert result == []


@pytest.mark.curio
class TestAsyncFiltering:
    """Test async filtering operator."""
    
    async def test_basic_afiltering(self):
        result = await atransduce(identity, async_from_iterable([1, 2, 3, 4, 5]), afiltering(lambda x: x % 2 == 0)(aappending()))
        assert result == [2, 4]
    
    async def test_filter_none(self):
        result = await atransduce(identity, async_from_iterable([1, 3, 5]), afiltering(lambda x: x % 2 == 0)(aappending()))
        assert result == []