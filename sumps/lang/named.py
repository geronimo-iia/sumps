from __future__ import annotations

from typing import Literal, Protocol

__all__ = ["Named", "Visibility", "is_public", "is_private", "match_visibility", "full_qualified_name"]


class Named(Protocol):
    """Define named item."""

    name: str


type Visibility = Literal["public", "private"]


def is_public(name: str) -> bool:
    return not name.startswith("_")


def is_private(name: str) -> bool:
    return name.startswith("_")


def match_visibility(name: str, visibility: Visibility) -> bool:
    return is_public(name=name) if visibility == "public" else is_private(name=name)


def full_qualified_name(f) -> str:
    """returns qualified name"""
    return f.__module__ + "." + f.__qualname__
