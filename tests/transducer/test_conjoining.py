"""Tests for conjoining operators."""

import pytest
from sumps.transducer import transduce, atransduce
# Simple identity function for tests
identity = lambda x: x
from sumps.transducer.operator import conjoining, aconjoining
from sumps.transducer.operator.async_utils import async_from_iterable


class TestConjoining:
    """Test sync conjoining operator."""
    
    def test_basic_conjoining(self):
        result = transduce(identity, [1, 2, 3], conjoining())
        assert result == (1, 2, 3)
    
    def test_empty_input(self):
        result = transduce(identity, [], conjoining())
        assert result == ()


@pytest.mark.curio
class TestAsyncConjoining:
    """Test async conjoining operator."""
    
    async def test_basic_aconjoining(self):
        result = await atransduce(identity, async_from_iterable([1, 2, 3]), aconjoining())
        assert result == (1, 2, 3)
    
    async def test_empty_input(self):
        result = await atransduce(identity, async_from_iterable([]), aconjoining())
        assert result == ()