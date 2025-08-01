"""Transducer operators for composable data transformation and collection.

This module provides a comprehensive set of transducer operators that can be
composed together to create efficient, single-pass data processing pipelines.
All operators follow the transducer protocol with proper type safety and
robust error handling.

## Collection Operators
- `appending()` - Collect items into a mutable list (most common)
- `conjoining()` - Collect items into an immutable tuple

## Transformation Operators  
- `mapping(transform)` - Transform each item using a function
- `filtering(predicate)` - Keep only items matching a predicate
- `enumerating(start=0)` - Add indices to items as (index, item) tuples
- `repeating(n)` - Repeat each item n times
- `batching(size)` - Group items into fixed-size batches

## Selection Operators
- `take(n)` - Take first n items, then terminate
- `drop(n)` - Skip first n items, process the rest
- `take_last(n)` - Keep only last n items from result
- `drop_last(n)` - Remove last n items from result
- `first_true(predicate)` - Take first item matching predicate
- `nth(n, default)` - Take only the nth item (1-indexed)

## Validation Operators
- `expecting_single()` - Ensure exactly one item is processed

## Usage Examples

### Basic Pipeline
```python
from sumps.transducer import transduce, mapping, filtering, appending

# Transform and filter in single pass
result = transduce(
    mapping(lambda x: x * 2) | filtering(lambda x: x > 10),
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    appending()
)
# Result: [12, 14, 16, 18, 20]
```

### Complex Composition
```python
from sumps.transducer import transduce, enumerating, batching, take

# Enumerate, batch, and limit
result = transduce(
    enumerating(1) | batching(3) | take(2),
    ['a', 'b', 'c', 'd', 'e', 'f', 'g'],
    appending()
)
# Result: [[(1, 'a'), (2, 'b'), (3, 'c')], [(4, 'd'), (5, 'e'), (6, 'f')]]
```

### Memory-Efficient Processing
```python
# Process large datasets without intermediate collections
result = transduce(
    filtering(lambda x: x % 2 == 0) | mapping(str) | take_last(3),
    range(1000000),  # Large input
    appending()
)
# Only keeps last 3 even numbers as strings
```

## Key Benefits
- **Composable**: Chain operators with `|` or function composition
- **Type Safe**: Full generic typing with proper inference
- **Memory Efficient**: Single-pass processing, no intermediate collections
- **Early Termination**: Operators like `take()` can stop processing early
- **Robust**: Comprehensive error handling and edge case management
"""

from .appending import Appending, appending, AsyncAppending, aappending
from .batching import Batching, batching, AsyncBatching, abatching
from .conjoining import Conjoining, conjoining, AsyncConjoining, aconjoining
from .enumerating import Enumerating, enumerating, AsyncEnumerating, aenumerating
from .expecting_single import ExpectingSingle, expecting_single, AsyncExpectingSingle, aexpecting_single
from .filtering import Filtering, filtering, AsyncFiltering, afiltering
from .drop_last import DropLast, drop_last, AsyncDropLast, adrop_last
from .take import Take, take, AsyncTake, atake
from .drop import Drop, drop, AsyncDrop, adrop
from .first_true import FirstTrue, first_true, AsyncFirstTrue, afirst_true
from .nth import Nth, nth, AsyncNth, anth
from .mapping import Mapping, mapping, AsyncMapping, async_mapping
from .repeating import Repeating, repeating, AsyncRepeating, arepeating
from .take_last import TakeLast, take_last, AsyncTakeLast, atake_last


# Collection operators
__all__ = [
    "Appending", "appending",          # Collect into mutable list
    "Conjoining", "conjoining",        # Collect into immutable tuple
    "AsyncConjoining", "aconjoining",   # Async collect into immutable tuple
    
    # Transformation operators
    "Mapping", "mapping",              # Transform items with function
    "Filtering", "filtering",          # Filter items with predicate
    "Enumerating", "enumerating",      # Add indices to items
    "AsyncEnumerating", "aenumerating",  # Async add indices to items
    "Repeating", "repeating",          # Repeat each item n times
    "AsyncRepeating", "arepeating",     # Async repeat each item n times
    "Batching", "batching",            # Group into fixed-size batches
    "AsyncBatching", "abatching",       # Async group into fixed-size batches
    
    # Selection operators
    "Take", "take",                    # Take first n items
    "Drop", "drop",                    # Skip first n items
    "AsyncDrop", "adrop",               # Async skip first n items
    "TakeLast", "take_last",           # Keep last n items
    "AsyncTakeLast", "atake_last",      # Async keep last n items
    "DropLast", "drop_last",           # Remove last n items
    "AsyncDropLast", "adrop_last",      # Async remove last n items
    "FirstTrue", "first_true",         # Take first matching item
    "AsyncFirstTrue", "afirst_true",    # Async take first matching item
    "Nth", "nth",                      # Take nth item (1-indexed)
    "AsyncNth", "anth",                 # Async take nth item (1-indexed)
    
    # Validation operators
    "ExpectingSingle", "expecting_single",  # Ensure exactly one item
    "AsyncExpectingSingle", "aexpecting_single",  # Async ensure exactly one item
    
    # Async operators
    "AsyncAppending", "aappending",         # Async list collection
    "AsyncMapping", "async_mapping",        # Async item transformation
    "AsyncFiltering", "afiltering",         # Async item filtering
    "AsyncTake", "atake",                   # Async take first n items
]