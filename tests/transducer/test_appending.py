"""Tests for appending operators."""

import pytest
from sumps.transducer import transduce, atransduce
from sumps.func import identity
from sumps.transducer.operator import appending, aappending
from sumps.transducer.operator.async_utils import async_from_iterable


class TestAppending:
    """Test sync appending operator."""
    
    def test_basic_appending(self):
        result = transduce(identity, [1, 2, 3], appending())
        assert result == [1, 2, 3]
    
    def test_empty_input(self):
        result = transduce(identity, [], appending())
        assert result == []


@pytest.mark.curio
class TestAsyncAppending:
    """Test async appending operator."""
    
    async def test_basic_aappending(self):
        result = await atransduce(identity, async_from_iterable([1, 2, 3]), aappending())
        assert result == [1, 2, 3]
    
    async def test_empty_input(self):
        result = await atransduce(identity, async_from_iterable([]), aappending())
        assert result == []