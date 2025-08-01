from sumps.lang import singleton


@singleton
class CounterDecorated:
    def __init__(self):
        self.count = 0

    def inc(self):
        self.count += 1


def test_singleton():
    a = CounterDecorated()
    b = CounterDecorated()
    assert a != b  # shared state did not mean shared instance
    assert a.count == b.count
    a.inc()
    assert a.count == b.count
    b.inc()
    assert a.count == b.count == 2
    
    # Create third instance to ensure orig_init is None
    c = CounterDecorated()
    assert c.count == 2  # Should have shared state, init not called again


def test_singleton_init_called_once():
    """Test that __init__ is only called once across multiple instances."""
    
    @singleton
    class InitTracker:
        def __init__(self):
            if hasattr(self, 'init_count'):
                self.init_count += 1
            else:
                self.init_count = 1
    
    # First instance - init should be called
    a = InitTracker()
    assert a.init_count == 1
    
    # Second instance - init should NOT be called again
    b = InitTracker()
    assert b.init_count == 1  # Still 1, not 2
    assert a.init_count == 1  # Shared state


def test_singleton_with_args():
    """Test singleton with __init__ arguments."""
    
    @singleton
    class WithArgs:
        def __init__(self, value):
            self.value = value
    
    a = WithArgs(42)
    assert a.value == 42
    
    # Second instance with different args - should share state
    b = WithArgs(99)  # This arg is ignored since init only called once
    assert b.value == 42  # Still has original value
    assert a.value == b.value
