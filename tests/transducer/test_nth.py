"""Tests for nth operators."""

import pytest
from sumps.transducer import transduce, atransduce
# Simple identity function for tests
identity = lambda x: x
from sumps.transducer.operator import nth, anth, appending, aappending
from sumps.transducer.operator.async_utils import async_from_iterable


class TestNth:
    """Test sync nth operator."""
    
    def test_basic_nth(self):
        result = transduce(identity, [1, 2, 3, 4], nth(3)(appending()))
        assert result == [3]
    
    def test_nth_with_default(self):
        result = transduce(identity, [1, 2], nth(5, 'missing')(appending()))
        assert result == ['missing']


@pytest.mark.curio
class TestAsyncNth:
    """Test async nth operator."""
    
    async def test_basic_anth(self):
        result = await atransduce(identity, async_from_iterable([1, 2, 3, 4]), anth(3)(aappending()))
        assert result == [3]
    
    async def test_nth_with_default(self):
        result = await atransduce(identity, async_from_iterable([1, 2]), anth(5, 'missing')(aappending()))
        assert result == ['missing']