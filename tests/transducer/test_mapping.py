"""Tests for mapping operators."""

import pytest
from sumps.transducer import transduce, atransduce
# Simple identity function for tests
identity = lambda x: x
from sumps.transducer.operator import mapping, async_mapping, appending, aappending
from sumps.transducer.operator.async_utils import async_from_iterable


class TestMapping:
    """Test sync mapping operator."""
    
    def test_basic_mapping(self):
        result = transduce(identity, [1, 2, 3], mapping(lambda x: x * 2)(appending()))
        assert result == [2, 4, 6]
    
    def test_string_mapping(self):
        result = transduce(identity, ['a', 'b'], mapping(str.upper)(appending()))
        assert result == ['A', 'B']


@pytest.mark.curio
class TestAsyncMapping:
    """Test async mapping operator."""
    
    async def test_basic_async_mapping(self):
        result = await atransduce(identity, async_from_iterable([1, 2, 3]), async_mapping(lambda x: x * 2)(aappending()))
        assert result == [2, 4, 6]
    
    async def test_string_mapping(self):
        result = await atransduce(identity, async_from_iterable(['a', 'b']), async_mapping(str.upper)(aappending()))
        assert result == ['A', 'B']