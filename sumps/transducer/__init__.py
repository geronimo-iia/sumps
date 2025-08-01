"""Transducer Library - Composable Data Processing Pipeline.

From https://sixty-north.com/blog/series/understanding-transducers-through-python post series.

A comprehensive transducer implementation providing memory-efficient, composable data transformations
with both synchronous and asynchronous support.

## Key Features

### Core Advantages
- **Single-pass processing**: No intermediate collections, memory efficient
- **Uniform interface**: All transformations follow same protocol
- **Early termination**: Built-in support via Reduced wrapper
- **Stateful transformations**: Can maintain state across items
- **Resource cleanup**: complete() method for finalization
- **Composability**: Chain multiple transformations seamlessly

### Dual Runtime Support
- **Synchronous**: Standard Python iterables and functions
- **Asynchronous**: Full async/await support with curio and asyncio compatibility
- **Unified API**: Same interface for both sync and async operations

### Comprehensive Operators

#### Collection Operators
- `appending`/`aappending`: Collect items into lists
- `conjoining`/`aconjoining`: Collect items into tuples

#### Transformation Operators  
- `mapping`/`async_mapping`: Transform each item with a function
- `enumerating`/`aenumerating`: Add indices to items
- `batching`/`abatching`: Group items into fixed-size batches
- `repeating`/`arepeating`: Repeat each item multiple times

#### Filtering Operators
- `filtering`/`afiltering`: Keep items matching predicate
- `first_true`/`afirst_true`: Take first item matching predicate
- `expecting_single`/`aexpecting_single`: Ensure exactly one item

#### Selection Operators
- `take`/`atake`: Take first n items with early termination
- `drop`/`adrop`: Skip first n items
- `take_last`/`atake_last`: Keep only last n items
- `drop_last`/`adrop_last`: Remove last n items
- `nth`/`anth`: Select nth item (1-indexed) with default

### Usage Examples

```python
# Synchronous processing
from sumps.transducer import transduce, mapping, filtering, take, appending
from sumps.func import compose

result = transduce(
    compose(mapping(lambda x: x * 2), filtering(lambda x: x > 5), take(3)),
    range(10),
    appending()
)  # [6, 8, 10]

# Asynchronous processing  
from sumps.transducer import atransduce, async_mapping, afiltering, atake, aappending
from sumps.transducer.operator.async_utils import async_from_iterable

result = await atransduce(
    compose(async_mapping(lambda x: x * 2), afiltering(lambda x: x > 5), atake(3)),
    async_from_iterable(range(10)),
    aappending()
)  # [6, 8, 10]
```

### Type Safety
- Full generic type support with proper type annotations
- Type ignore comments where transformations change item types
- Protocol-based design for extensibility

### Testing
- Comprehensive test coverage with pytest
- Curio marker support for async tests
- Both sync and async variants tested
- Edge cases and error conditions covered

"""

from .base import Predicate, Reduced, Transducer, AsyncTransducer, BaseTransducer, BaseAsyncTransducer, SizedResult, Transform, is_reducer
from .operator import (
    # Sync operators
    appending, batching, conjoining, enumerating, expecting_single, filtering,
    drop_last, take, first_true, drop, nth, mapping, repeating, take_last,
    # Async operators  
    aappending, abatching, aconjoining, adrop, adrop_last, aenumerating,
    aexpecting_single, afirst_true, anth, arepeating, atake, atake_last,
    async_mapping, afiltering
)
from .transduce import transduce, atransduce

__all__ = [
    # Core types and protocols
    "Predicate",
    "Transform", 
    "Transducer",
    "AsyncTransducer",
    "BaseTransducer",
    "BaseAsyncTransducer",
    "SizedResult",
    "Reduced",
    "is_reducer",
    
    # Processing functions
    "transduce",
    "atransduce",
    
    # Collection operators
    "appending", "aappending",
    "conjoining", "aconjoining", 
    
    # Transformation operators
    "mapping", "async_mapping",
    "enumerating", "aenumerating",
    "batching", "abatching",
    "repeating", "arepeating",
    
    # Filtering operators
    "filtering", "afiltering",
    "first_true", "afirst_true",
    "expecting_single", "aexpecting_single",
    
    # Selection operators
    "take", "atake",
    "drop", "adrop", 
    "take_last", "atake_last",
    "drop_last", "adrop_last",
    "nth", "anth",
]
