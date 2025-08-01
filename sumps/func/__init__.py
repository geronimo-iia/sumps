"""Functional Programming Utilities - Higher-Order Functions and Combinators.

A comprehensive collection of functional programming utilities providing function composition,
currying, memoization, and other higher-order function operations.

## Key Features

### Function Composition
- **compose**: Right-to-left function composition with async support
- **pipe**: Left-to-right function composition (more intuitive ordering)
- **Dynamic compilation**: Optimized code generation for composed functions
- **Hybrid async/sync**: Automatic detection and handling of async functions

### Function Transformation
- **curried**: Transform functions to support partial application
- **closure**: Create closures with captured variables
- **call_once**: Memoization wrapper that caches single function call
- **identity**: Simple identity function for functional pipelines

### Advanced Features
- **Signature preservation**: Maintains original function signatures
- **Type safety**: Full generic type support
- **Lambda support**: Works with lambda functions and closures
- **Performance optimization**: Dynamic code generation for efficiency

## Usage Examples

### Function Composition
```python
from sumps.func import compose, pipe

# Right-to-left composition (mathematical style)
add_then_double = compose(lambda x: x * 2, lambda x: x + 1)
result = add_then_double(5)  # (5 + 1) * 2 = 12

# Left-to-right composition (pipeline style)
double_then_add = pipe(lambda x: x * 2, lambda x: x + 1)
result = double_then_add(5)  # (5 * 2) + 1 = 11

# Async function composition
async def async_add(x): return x + 1
async def async_double(x): return x * 2

async_pipeline = compose(async_double, async_add)
result = await async_pipeline(5)  # 12
```

### Currying and Partial Application
```python
from sumps.func import curried

@curried
def add_three(a, b, c):
    return a + b + c

# Partial application
add_5_and = add_three(5)  # Partially applied
result = add_5_and(3, 2)  # 5 + 3 + 2 = 10

# Full currying
fully_curried = add_three(1)(2)(3)  # 6
```

### Memoization and Optimization
```python
from sumps.func import call_once, closure

# Single-call memoization
@call_once
def expensive_computation():
    return sum(range(1000000))

result1 = expensive_computation()  # Computed
result2 = expensive_computation()  # Cached

# Closure creation
counter = closure(lambda: {'count': 0})
increment = closure(lambda state: state.update(count=state['count'] + 1))
```

## Integration with Transducers
```python
from sumps.func import compose, identity
from sumps.transducer import transduce, mapping, filtering, appending

# Compose transducers with func utilities
process_data = compose(
    mapping(lambda x: x * 2),
    filtering(lambda x: x > 10)
)

result = transduce(process_data, range(10), appending())
```

## Design Philosophy
- **Composability**: All functions designed to work together seamlessly
- **Performance**: Dynamic compilation where beneficial
- **Simplicity**: Clean, intuitive APIs
- **Flexibility**: Support for both sync and async operations

"""

from .call_once import call_once
from .closure import closure
from .compose import compose, pipe
from .curried import curried
from .identity import identity

__all__ = [
    # Function composition
    "compose",      # Right-to-left function composition
    "pipe",         # Left-to-right function composition
    
    # Function transformation
    "curried",      # Enable partial application
    "closure",      # Create closures with captured state
    "call_once",    # Single-call memoization
    "identity",     # Identity function
]
