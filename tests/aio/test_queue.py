"""Test module for sumps.aio.queue."""

import pytest
from curio import CancelledError, LifoQueue, PriorityQueue, Queue, UniversalQueue, run

from sumps.aio.queue import QueueIterator, UniversalQueueIterator, iter


class TestQueueIterator:
    """Test QueueIterator class."""

    @pytest.fixture
    def queue(self):
        """Create a test queue."""
        return Queue()

    @pytest.fixture
    def iterator(self, queue):
        """Create a test iterator."""
        return QueueIterator(queue)

    def test_init(self, queue):
        """Test iterator initialization."""
        iterator = QueueIterator(queue)
        assert iterator.queue is queue
        assert iterator._halt is False

    def test_aiter(self, iterator):
        """Test async iterator protocol."""
        assert iterator.__aiter__() is iterator

    @pytest.mark.curio
    async def test_anext_with_items(self):
        """Test async iteration with items."""
        queue = Queue()
        iterator = QueueIterator(queue)
        
        await queue.put("item1")
        await queue.put("item2")
        await queue.put(None)  # Stop signal
        
        items = []
        async for item in iterator:
            items.append(item)
        
        assert items == ["item1", "item2"]

    @pytest.mark.curio
    async def test_anext_empty_stops(self):
        """Test that empty item stops iteration."""
        queue = Queue()
        iterator = QueueIterator(queue)
        
        await queue.put(None)
        
        with pytest.raises(StopAsyncIteration):
            await iterator.__anext__()

    @pytest.mark.curio
    async def test_halt_stops_iteration(self):
        """Test halt method stops iteration."""
        queue = Queue()
        iterator = QueueIterator(queue)
        
        await iterator.halt()
        
        with pytest.raises(StopAsyncIteration):
            await iterator.__anext__()

    @pytest.mark.curio
    async def test_cancelled_error_stops_iteration(self):
        """Test CancelledError stops iteration."""
        queue = Queue()
        iterator = QueueIterator(queue)
        
        # Mock queue.get to raise CancelledError
        async def mock_get():
            raise CancelledError()
        
        queue.get = mock_get
        
        with pytest.raises(StopAsyncIteration):
            await iterator.__anext__()


class TestUniversalQueueIterator:
    """Test UniversalQueueIterator class."""

    @pytest.fixture
    def queue(self):
        """Create a test universal queue."""
        return UniversalQueue()

    @pytest.fixture
    def iterator(self, queue):
        """Create a test iterator."""
        return UniversalQueueIterator(queue)

    def test_init(self, queue):
        """Test iterator initialization."""
        iterator = UniversalQueueIterator(queue)
        assert iterator.queue is queue
        assert iterator._halt is False

    def test_aiter(self, iterator):
        """Test async iterator protocol."""
        assert iterator.__aiter__() is iterator

    def test_iter(self, iterator):
        """Test sync iterator protocol."""
        assert iterator.__iter__() is iterator

    def test_next_with_items(self):
        """Test sync iteration with items."""
        queue = UniversalQueue()
        iterator = UniversalQueueIterator(queue)
        
        queue.put("item1")
        queue.put("item2")
        queue.put(None)  # Stop signal
        
        items = []
        try:
            while True:
                items.append(next(iterator))
        except StopIteration:
            pass
        
        assert items == ["item1", "item2"]

    def test_next_empty_stops(self):
        """Test that empty item stops sync iteration."""
        queue = UniversalQueue()
        iterator = UniversalQueueIterator(queue)
        
        queue.put(None)
        
        with pytest.raises(StopIteration):
            next(iterator)

    def test_halt_stops_sync_iteration(self):
        """Test halt method stops sync iteration."""
        queue = UniversalQueue()
        iterator = UniversalQueueIterator(queue)
        
        iterator.halt()
        
        with pytest.raises(StopIteration):
            next(iterator)

    @pytest.mark.curio
    async def test_anext_with_items(self):
        """Test async iteration with items."""
        queue = UniversalQueue()
        iterator = UniversalQueueIterator(queue)
        
        await queue.put("item1")
        await queue.put("item2")
        await queue.put(None)  # Stop signal
        
        items = []
        async for item in iterator:
            items.append(item)
        
        assert items == ["item1", "item2"]

    @pytest.mark.curio
    async def test_halt_stops_async_iteration(self):
        """Test halt method stops async iteration."""
        queue = UniversalQueue()
        iterator = UniversalQueueIterator(queue)
        
        await iterator.halt()
        
        with pytest.raises(StopAsyncIteration):
            await iterator.__anext__()

    def test_sync_cancelled_error_stops_iteration(self):
        """Test CancelledError stops sync iteration."""
        queue = UniversalQueue()
        iterator = UniversalQueueIterator(queue)
        
        # Mock queue.get to raise CancelledError
        def mock_get():
            raise CancelledError()
        
        queue.get = mock_get
        
        with pytest.raises(StopIteration):
            next(iterator)

    @pytest.mark.curio
    async def test_async_cancelled_error_stops_iteration(self):
        """Test CancelledError stops async iteration."""
        queue = UniversalQueue()
        iterator = UniversalQueueIterator(queue)
        
        # Mock queue.get to raise CancelledError
        async def mock_get():
            raise CancelledError()
        
        queue.get = mock_get
        
        with pytest.raises(StopAsyncIteration):
            await iterator.__anext__()


class TestIterFunction:
    """Test iter function."""

    def test_iter_with_simple_queue(self):
        """Test iter function with simple queue types."""
        queue = Queue()
        iterator = iter(queue)
        assert isinstance(iterator, QueueIterator)
        assert iterator.queue is queue

    def test_iter_with_priority_queue(self):
        """Test iter function with PriorityQueue."""
        queue = PriorityQueue()
        iterator = iter(queue)
        assert isinstance(iterator, QueueIterator)
        assert iterator.queue is queue

    def test_iter_with_lifo_queue(self):
        """Test iter function with LifoQueue."""
        queue = LifoQueue()
        iterator = iter(queue)
        assert isinstance(iterator, QueueIterator)
        assert iterator.queue is queue

    def test_iter_with_universal_queue(self):
        """Test iter function with UniversalQueue."""
        queue = UniversalQueue()
        iterator = iter(queue)
        assert isinstance(iterator, UniversalQueueIterator)
        assert iterator.queue is queue


class TestIntegration:
    """Integration tests."""

    @pytest.mark.curio
    async def test_queue_iterator_integration(self):
        """Test QueueIterator with actual curio queue."""
        async def producer(queue):
            for i in range(3):
                await queue.put(f"item{i}")
            await queue.put(None)  # Stop signal

        async def consumer(queue):
            items = []
            async for item in iter(queue):
                items.append(item)
            return items

        queue = Queue()
        await producer(queue)
        items = await consumer(queue)
        
        assert items == ["item0", "item1", "item2"]

    @pytest.mark.curio
    async def test_universal_queue_iterator_integration(self):
        """Test UniversalQueueIterator with actual curio queue."""
        async def producer(queue):
            for i in range(3):
                await queue.put(f"item{i}")
            await queue.put(None)  # Stop signal

        async def consumer(queue):
            items = []
            async for item in iter(queue):
                items.append(item)
            return items

        queue = UniversalQueue()
        await producer(queue)
        items = await consumer(queue)
        
        assert items == ["item0", "item1", "item2"]