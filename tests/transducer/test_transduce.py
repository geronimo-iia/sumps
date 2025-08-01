"""Tests for transduce and atransduce core functions."""

import pytest
from sumps.transducer import transduce, atransduce, Reduced
from sumps.transducer.operator import appending, aappending, mapping, async_mapping
from sumps.transducer.operator.async_utils import async_from_iterable
from sumps.func import identity


class TestTransduce:
    """Test sync transduce function."""
    
    def test_basic_transduce(self):
        result = transduce(identity, [1, 2, 3], appending())
        assert result == [1, 2, 3]
    
    def test_transduce_with_transform(self):
        result = transduce(mapping(lambda x: x * 2), [1, 2, 3], appending())
        assert result == [2, 4, 6]
    
    def test_transduce_with_init(self):
        result = transduce(identity, [1, 2, 3], appending(), [0])
        assert result == [0, 1, 2, 3]
    
    def test_transduce_empty_input(self):
        result = transduce(identity, [], appending())
        assert result == []
    
    def test_transduce_default_reducer(self):
        result = transduce(identity, [1, 2, 3])
        assert result == [1, 2, 3]
    
    def test_transduce_early_termination(self):
        def early_term_reducer():
            class EarlyTerm:
                def initial(self): return []
                def step(self, result, item):
                    result.append(item)
                    return Reduced(result) if len(result) >= 2 else result
                def complete(self, result): return result
            return EarlyTerm()
        
        result = transduce(identity, [1, 2, 3, 4, 5], early_term_reducer())
        assert result == [1, 2]


@pytest.mark.curio
class TestAsyncTransduce:
    """Test async atransduce function."""
    
    async def test_basic_atransduce(self):
        result = await atransduce(identity, async_from_iterable([1, 2, 3]), aappending())
        assert result == [1, 2, 3]
    
    async def test_atransduce_with_transform(self):
        result = await atransduce(async_mapping(lambda x: x * 2), async_from_iterable([1, 2, 3]), aappending())
        assert result == [2, 4, 6]
    
    async def test_atransduce_with_init(self):
        result = await atransduce(identity, async_from_iterable([1, 2, 3]), aappending(), [0])
        assert result == [0, 1, 2, 3]
    
    async def test_atransduce_empty_input(self):
        result = await atransduce(identity, async_from_iterable([]), aappending())
        assert result == []
    
    async def test_atransduce_default_reducer(self):
        result = await atransduce(identity, async_from_iterable([1, 2, 3]))
        assert result == [1, 2, 3]
    
    async def test_atransduce_early_termination(self):
        class AsyncEarlyTerm:
            async def initial(self): return []
            async def step(self, result, item):
                result.append(item)
                return Reduced(result) if len(result) >= 2 else result
            async def complete(self, result): return result
        
        result = await atransduce(identity, async_from_iterable([1, 2, 3, 4, 5]), AsyncEarlyTerm())
        assert result == [1, 2]