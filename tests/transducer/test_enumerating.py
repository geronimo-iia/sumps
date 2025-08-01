"""Tests for enumerating operators."""

import pytest
from sumps.transducer import transduce, atransduce
# Simple identity function for tests
identity = lambda x: x
from sumps.transducer.operator import enumerating, aenumerating, appending, aappending
from sumps.transducer.operator.async_utils import async_from_iterable


class TestEnumerating:
    """Test sync enumerating operator."""
    
    def test_basic_enumerating(self):
        result = transduce(identity, ['a', 'b', 'c'], enumerating()(appending()))
        assert result == [(0, 'a'), (1, 'b'), (2, 'c')]
    
    def test_custom_start(self):
        result = transduce(identity, ['x', 'y'], enumerating(10)(appending()))
        assert result == [(10, 'x'), (11, 'y')]


@pytest.mark.curio
class TestAsyncEnumerating:
    """Test async enumerating operator."""
    
    async def test_basic_aenumerating(self):
        result = await atransduce(identity, async_from_iterable(['a', 'b', 'c']), aenumerating()(aappending()))
        assert result == [(0, 'a'), (1, 'b'), (2, 'c')]
    
    async def test_custom_start(self):
        result = await atransduce(identity, async_from_iterable(['x', 'y']), aenumerating(10)(aappending()))
        assert result == [(10, 'x'), (11, 'y')]