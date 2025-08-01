"""functions related operator."""

from .call_once import call_once
from .closure import closure
from .compose import compose, pipe
from .curried import curried
from .identity import identity

__all__ = ["closure", "compose", "pipe", "curried", "identity", "call_once"]
