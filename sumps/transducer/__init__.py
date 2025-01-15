"""Transducer.

From https://sixty-north.com/blog/series/understanding-transducers-through-python post series.

"""

from .batching import batching
from .enumerating import enumerating
from .filtering import filtering
from .iters import drop, first_true, nth, take
from .mapping import mapping
from .model import Predicate, Reduced, Transducer, Transform, is_reducer
from .reducer import appending, conjoining, drop_last, expecting_single, take_last
from .repeating import repeating
from .transduce import transduce

__all__ = [
    "Predicate",
    "Transform",
    "Transducer",
    "Reduced",
    "is_reducer",
    "batching",
    "enumerating",
    "filtering",
    "take",
    "first_true",
    "drop",
    "nth",
    "mapping",
    "appending",
    "conjoining",
    "expecting_single",
    "drop_last",
    "take_last",
    "repeating",
    "transduce",
]
