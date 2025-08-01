"""Tests for first_true operators."""

import pytest
from sumps.transducer import transduce, atransduce
# Simple identity function for tests
identity = lambda x: x
from sumps.transducer.operator import first_true, afirst_true, appending, aappending
from sumps.transducer.operator.async_utils import async_from_iterable


class TestFirstTrue:
    """Test sync first_true operator."""
    
    def test_basic_first_true(self):
        result = transduce(identity, [1, 3, 4, 6], first_true(lambda x: x % 2 == 0)(appending()))
        assert result == [4]
    
    def test_no_match(self):
        result = transduce(identity, [1, 3, 5], first_true(lambda x: x % 2 == 0)(appending()))
        assert result == []


@pytest.mark.curio
class TestAsyncFirstTrue:
    """Test async first_true operator."""
    
    async def test_basic_afirst_true(self):
        result = await atransduce(identity, async_from_iterable([1, 3, 4, 6]), afirst_true(lambda x: x % 2 == 0)(aappending()))
        assert result == [4]
    
    async def test_no_match(self):
        result = await atransduce(identity, async_from_iterable([1, 3, 5]), afirst_true(lambda x: x % 2 == 0)(aappending()))
        assert result == []