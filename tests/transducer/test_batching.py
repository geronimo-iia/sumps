"""Tests for batching operators."""

import pytest
from sumps.transducer import transduce, atransduce
# Simple identity function for tests
identity = lambda x: x
from sumps.transducer.operator import batching, abatching, appending, aappending
from sumps.transducer.operator.async_utils import async_from_iterable


class TestBatching:
    """Test sync batching operator."""
    
    def test_basic_batching(self):
        result = transduce(identity, [1, 2, 3, 4, 5], batching(2)(appending()))
        assert result == [[1, 2], [3, 4], [5]]
    
    def test_exact_batches(self):
        result = transduce(identity, [1, 2, 3, 4], batching(2)(appending()))
        assert result == [[1, 2], [3, 4]]


@pytest.mark.curio
class TestAsyncBatching:
    """Test async batching operator."""
    
    async def test_basic_abatching(self):
        result = await atransduce(identity, async_from_iterable([1, 2, 3, 4, 5]), abatching(2)(aappending()))
        assert result == [[1, 2], [3, 4], [5]]
    
    async def test_exact_batches(self):
        result = await atransduce(identity, async_from_iterable([1, 2, 3, 4]), abatching(2)(aappending()))
        assert result == [[1, 2], [3, 4]]