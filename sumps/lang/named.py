from __future__ import annotations

from typing import Literal, Protocol, runtime_checkable

__all__ = ["Named", "Visibility", "is_public", "is_private", "match_visibility"]


@runtime_checkable
class Named(Protocol):
    """Protocol for an item with a name."""

    @property
    def name(self) -> str: ...


type Visibility = Literal["public", "private"]


def is_public(name: str) -> bool:
    """Return True if the name follows the public naming convention (does NOT start with underscore)."""
    return not name.startswith("_")


def is_private(name: str) -> bool:
    """Return True if the name follows the private naming convention (starts with underscore)."""
    return name.startswith("_")


def match_visibility(name: str, visibility: Visibility) -> bool:
    """Return True if the name matches the given visibility."""
    checker = is_public if visibility == "public" else is_private
    return checker(name=name)
