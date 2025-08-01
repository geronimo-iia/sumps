"""Tests for expecting_single operators."""

import pytest
from sumps.transducer import transduce, atransduce
# Simple identity function for tests
identity = lambda x: x
from sumps.transducer.operator import expecting_single, aexpecting_single, appending, aappending
from sumps.transducer.operator.async_utils import async_from_iterable


class TestExpectingSingle:
    """Test sync expecting_single operator."""
    
    def test_single_item(self):
        result = transduce(identity, [42], expecting_single()(appending()))
        assert result == [42]
    
    def test_multiple_items_raises(self):
        with pytest.raises(RuntimeError, match="Too many steps"):
            transduce(identity, [1, 2], expecting_single()(appending()))
    
    def test_no_items_raises(self):
        with pytest.raises(RuntimeError, match="Too few steps"):
            transduce(identity, [], expecting_single()(appending()))


@pytest.mark.curio
class TestAsyncExpectingSingle:
    """Test async expecting_single operator."""
    
    async def test_single_item(self):
        result = await atransduce(identity, async_from_iterable([42]), aexpecting_single()(aappending()))
        assert result == [42]
    
    async def test_multiple_items_raises(self):
        with pytest.raises(RuntimeError, match="Too many steps"):
            await atransduce(identity, async_from_iterable([1, 2]), aexpecting_single()(aappending()))
    
    async def test_no_items_raises(self):
        with pytest.raises(RuntimeError, match="Too few steps"):
            await atransduce(identity, async_from_iterable([]), aexpecting_single()(aappending()))