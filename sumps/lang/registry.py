from __future__ import annotations

from collections.abc import Iterable
from typing import Generic, Protocol, TypeVar

from msgspec import Struct, field

from .named import Named, Visibility, match_visibility

__all__ = ["NamedItem", "RegisterHandler", "Dictionary"]


# -------------------------
# Type Variables
# -------------------------

NamedItem = TypeVar("NamedItem", bound=Named)
InputItem = TypeVar("InputItem", bound=Named, contravariant=True)


# -------------------------
# Dictionary of Named Items
# -------------------------


class Dictionary(Struct, Generic[NamedItem]):
    """Implements a dictionary of named items with optional immutability."""

    # Internal mapping from item name to item
    _items: dict[str, NamedItem] = field(default_factory=dict)
    # Flag to prevent further modification (e.g., after initialization)
    _frozen: bool = False

    def exists(self, name: str) -> bool:
        """Check if an item with the given name exists in the dictionary."""
        return name in self._items

    def add(self, item: NamedItem) -> None:
        """Add a new item to the dictionary. Raises if frozen."""
        if self._frozen:
            raise RuntimeError("Frozen instance") from None
        self._items[item.name] = item

    def remove(self, name: str) -> NamedItem:
        """
        Remove an item by name and return it.
        Raises KeyError if not found.
        Raises RuntimeError if frozen.
        """
        if self._frozen:
            raise RuntimeError("Frozen instance") from None
        try:
            return self._items.pop(name)
        except KeyError as e:
            raise KeyError(f"No item named '{name}' found in registry.") from e

    def all(self) -> Iterable[NamedItem]:
        """Yield all items in the dictionary."""
        yield from self._items.values()

    def filter(self, visibility: Visibility) -> Iterable[NamedItem]:
        """
        Filter items based on a visibility constraint using naming conventions.
        Assumes `match_visibility(name, visibility)` returns True if the name matches the visibility rule.
        """
        return filter(lambda s: match_visibility(name=s.name, visibility=visibility), self.all())

    def freeze(self) -> None:
        """Prevent further modification of the dictionary."""
        self._frozen = True

    def frozen(self) -> bool:
        """Check if the dictionary has been frozen."""
        return self._frozen

    def get(self, name: str) -> NamedItem | None:
        return self._items.get(name)

    def __getitem__(self, name: str) -> NamedItem:
        return self._items[name]


# ----------------------------------------
# Protocol for functions that register items
# ----------------------------------------


class RegisterHandler(Protocol, Generic[InputItem]):
    """Define a callable handler to register (add) an item into a registry."""

    def __call__(self, item: InputItem) -> None: ...


# ---------------------------
# Registry built on Dictionary
# ---------------------------


class Registry(Dictionary, Generic[NamedItem]):
    """A named item registry with an exposed handler-compatible `add` method."""

    def handler(self) -> RegisterHandler[NamedItem]:
        """
        Return the `add` method as a `RegisterHandler` so it can be passed
        to other components expecting that interface.
        """
        return self.add
