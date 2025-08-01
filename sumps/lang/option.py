"""
Rust [Option](https://doc.rust-lang.org/std/option/) implementation.

This work is based on [Peijun Ma](https://github.com/MaT1g3R/option).

An Option type represents an optional value, every Option is either Some and contains Some value, or Nothing.
Using an Option type forces you to deal with None values in your code and increase type safety.

Nothing as the meaning of python None, msgspec UNSET.



Purpose: Provide a type-safe way to express optional values, forcing users to handle the "empty" (Nothing) case explicitly.

Variants:
    Some(value) holds a value that is guaranteed not to be None or Nothing.
    Nothing() represents no value; it’s a singleton.
Main class: Option[T] - abstract base with all core logic.
Factory helpers: maybe(value), just(value) to create Option from values.

Extensive API:
    unwrap, expect, unwrap_or, unwrap_or_else
    map, map_or, map_or_else
    filter, zip, zip_with, unzip, flatten
    Boolean logic operators: __and__, __or__, __xor__
    Comparison operators with correct semantics (<, <=, >, >=)
    get for mapping keys inside an Option[Mapping]
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any, Generic, Protocol, TypeVar

from msgspec import UNSET

__all__ = ["maybe", "just", "Option", "Some", "Nothing"]

T = TypeVar("T", covariant=True)
U = TypeVar("U")
V = TypeVar("V")
R = TypeVar("R")


class LessThan(Protocol):
    def __lt__(self, other) -> bool: ...


class GreaterThan(Protocol):
    def __gt__(self, other) -> bool: ...


class LessOrEqual(Protocol):
    def __le__(self, other) -> bool: ...


class GreaterOrEqual(Protocol):
    def __ge__(self, other) -> bool: ...


class Option(Generic[T]):
    """Type Option represents an optional value:
    every Option is either Some and contains a value, or Nothing, and does not.

    All the operation logic are implemented at this class level, Nothing and Some class deal only with parameters.

    """

    __slots__ = ("_is_some", "_value", "_initialized")
    __match_args__ = "_value"

    def __new__(cls, is_some: bool, value: T):
        # only Some and Nothing can be instanciated.
        if cls == Some or cls == Nothing:  # noqa: SIM109
            instance = super().__new__(cls)
            instance._is_some = is_some
            instance._value = value
            instance._initialized = True  # Mark as initialized
            return instance
        raise RuntimeError("only Some or Nothing can be instanciated.")

    def __setattr__(self, name, value):
        if hasattr(self, "_initialized"):
            # Prevent attribute changes after initialization
            raise AttributeError(f"{type(self).__name__} is immutable")
        # Allow setting attributes during __new__ before _initialized is set
        super().__setattr__(name, value)

    def __delattr__(self, name):
        raise AttributeError(f"{type(self).__name__} is immutable")

    @property
    def is_some(self) -> bool:
        """Return true if the Option is Some."""
        return self._is_some

    @property
    def is_none(self) -> bool:
        """Return true if the Option is None (alias Nothing)."""
        return not self._is_some

    def __bool__(self) -> bool:
        """Return true if the Option is Some."""
        return self._is_some

    def expect(self, msg: str) -> T:
        """Returns the contained Some value, consuming the self value.

        Raise:
            (ValueError): if the value is a None with a custom panic message provided by msg.
        """
        if self._is_some:
            return self._value
        raise ValueError(msg)

    def unwrap(self) -> T:
        """Returns the contained Some value, consuming the self value.

        Raise:
            (ValueError) if the self value equals None.
        """
        return self.value

    @property
    def value(self) -> T:
        """Returns the contained Some value, consuming the self value.

        Raise:
            (ValueError) if the self value equals None.
        """
        if self._is_some:
            return self._value
        raise ValueError("Value is Nothing.")

    def unwrap_or(self, default: U) -> T | U:
        """Returns the contained Some value or a provided default."""
        return self._value if self._is_some else default

    def unwrap_or_else(self, callback: Callable[[], U]) -> T | U:
        """Returns the contained Some value or computes it from a closure."""
        return self._value if self._is_some else callback()

    def map(self, callback: Callable[[T], U]) -> Option[U]:
        """Maps an Option<T> to Option<U> by applying a function to a contained value (if Some)
        or returns None (if None)."""
        return maybe(callback(self._value)) if self._is_some else Nothing()

    def map_or(self, callback: Callable[[T], U], default: V) -> U | V:
        """Returns the provided default result (if none), or applies a function to the contained value (if any)."""
        return callback(self._value) if self._is_some else default

    def map_or_else(self, callback: Callable[[T], U], default: Callable[[], V]) -> U | V:
        """Computes a default function result (if none),
        or applies a different function to the contained value (if any)."""
        return callback(self._value) if self._is_some else default()

    def filter(self, predicate: Callable[[T], bool]) -> Option[T]:
        """
        Returns None if the option is None, otherwise calls predicate with the wrapped value and returns:

        Some(t) if predicate returns true (where t is the wrapped value), and
        None if predicate returns false.
        """
        if self._is_some and predicate(self._value):
            return self
        return Nothing()

    def zip(self, other: Option[U]) -> Option[tuple[T, U]]:
        """Zips self with another Option.

        If self is Some(s) and other is Some(o), this method returns Some((s, o)). Otherwise, Nothing is returned.
        """
        return self.zip_with(other=other, f=lambda a, b: (a, b)) if self._is_some else Nothing()

    def zip_with(self, other: Option[U], f: Callable[[T, U], R]) -> Option[R]:
        """
        Zips self and another Option with function f.

        If self is Some(s) and other is Some(o), this method returns Some(f(s, o)). Otherwise, Nothing is returned.
        """
        if self._is_some and other.is_some:
            return Some(value=f(self._value, other.value))
        return Nothing()

    def unzip(self) -> tuple[Option[Any], Option[Any]]:
        """Unzips an Option containing a 2-element tuple into a tuple of two Options.

        Returns:
            (Some(a), Some(b)) if self is Some((a, b)),
            (Nothing, Nothing) otherwise.
        """
        if self._is_some:
            val = self._value
            if isinstance(val, tuple) and len(val) == 2:
                return Some(val[0]), Some(val[1])
        return Nothing(), Nothing()

    def flatten(self) -> Option[T]:
        """Converts from Option[Option[T]] to Option[T]."""
        if isinstance(self._value, Option):
            return self._value
        # if isinstance(self._value, Some):
        #    return self._value
        return self

    def __hash__(self):
        return hash((self._is_some, self._value))

    def __repr__(self) -> str:
        return f"Some({self.value!r})" if self._is_some else "Nothing"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, type(self)) and self._is_some == other._is_some and self._value == other._value

    def __ne__(self, other: object) -> bool:
        return not self == other

    def __and__(self, optb: Option[U]) -> Option[U]:
        """Returns Nothing if this option is Nothing, otherwise returns optb."""
        return optb if self._is_some and optb._is_some else Nothing()

    def and_then(self, f: Callable[[T], U]) -> Option[U]:
        """Returns Nothing if this option is Nothing, otherwise calls f with the wrapped value and returns the result."""
        return Nothing() if self.is_none else maybe(value=f(self._value))

    def flatmap(self, f: Callable[[T], U]) -> Option[U]:
        """Alias of and_then."""
        return self.and_then(f=f)

    def bind(self, f: Callable[[T], U]) -> Option[U]:
        """Alias of and_then."""
        return self.and_then(f=f)

    def __or__(self, optb: Option[U]) -> Option[T | U]:
        """Returns the option if it contains a value, otherwise returns optb."""
        if self._is_some:
            return self
        return optb if optb._is_some else Nothing()

    def or_else(self, f: Callable[[], U]) -> Option[T | U]:
        """Returns the option if it contains a value, otherwise calls f and returns the result."""
        return self if self._is_some else maybe(value=f())

    def __xor__(self, optb: Option[U]) -> Option[T | U]:
        """Returns Some if exactly one of self, optb is Some, otherwise returns Nothing."""
        if self.is_none and optb.is_some:
            return optb
        if self.is_some and optb.is_none:
            return self
        return Nothing()

    def __lt__(self: Option[LessThan], other: Option[U]) -> bool:
        """This method tests less than (for self and other) and is used by the < operator."""
        if self.is_some:
            if other.is_some:
                return self.value < other.value
            return False
        return other.is_some

    def __le__(self: Option[LessOrEqual], other: Option[U]) -> bool:
        """This method tests less than or equal to (for self and other) and is used by the <= operator."""
        if self.is_some:
            if other.is_some:
                return self.value <= other.value
            return False
        return True

    def __gt__(self: Option[GreaterThan], other: Option[U]) -> bool:
        """This method tests greater than (for self and other) and is used by the > operator."""
        if self.is_some:
            if other.is_some:
                return self.value > other.value
            return True
        return False

    def __ge__(self: Option[GreaterOrEqual], other: Option[U]) -> bool:
        """This method tests greater than or equal to (for self and other) and is used by the >= operator."""
        if self.is_some:
            if other.is_some:
                return self.value >= other.value
            return True
        return other.is_none

    def get(self: Option[Mapping[U, V]], key: U, default: V | None = None) -> Option[V]:
        """
        Gets a mapping value by key in the contained value or returns
        ``default`` if the key doesn't exist.

        Args:
            key: The mapping key.
            default: The defauilt value.

        Returns:
            * ``Some`` variant of the mapping value if the key exists
               and the value is not None.
            * ``Some(default)`` if ``default`` is not None.
            * :py:data:`Nothing` if ``default`` is None.
        """
        if self._is_some:
            return maybe(self._value.get(key, default))
        return maybe(default)


class Some(Option[T]):
    def __new__(cls, value: T) -> Some[T]:
        if is_nothing(value):
            raise RuntimeError("Some cant be None or Nothing, you should use maybe(value).")
        return super().__new__(cls, is_some=True, value=value)


class Nothing(Option[Any]):
    """Nothing is the rust 'None'.

    Note: nothing is a classic singleton shared instance.
    """

    __match_args__ = ()  # No fields to match on

    def __new__(cls) -> Nothing:
        if not hasattr(cls, "__singleton"):
            cls.__singleton = super().__new__(cls, is_some=False, value=None)
        return cls.__singleton


# Factory functions
def some(value: T) -> Option[T]:
    return Some(value)


def nothing() -> Option[None]:
    return Nothing()


def maybe[T](value: T | None) -> Option[T]:
    if is_nothing(value=value):
        return Nothing()
    assert value is not None  # helper for type checking
    return Some(value=value)


def just[T](value: T) -> Option[T]:
    assert value is not None  # helper for type checking
    return Some(value=value)


def is_nothing(value) -> bool:
    """define nothing."""
    return value is None or value is UNSET or isinstance(value, Nothing)
