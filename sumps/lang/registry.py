from __future__ import annotations

from collections.abc import Iterable
from typing import Generic, Protocol, TypeVar

from msgspec import Struct, field

from .named import Named, Visibility, match_visibility

__all__ = ["NamedItem", "RegisterHandler", "Dictionary"]

NamedItem = TypeVar("NamedItem", bound=Named, contravariant=True)


class RegisterHandler(Protocol, Generic[NamedItem]):
    """Register an item."""

    def __call__(self, item: NamedItem): ...


class Dictionary(Struct, Generic[NamedItem]):
    """Implements a dictionnary of named items."""

    _items: dict[str, NamedItem] = field(default_factory=dict)
    _frozen: bool = False

    def exists(self, name: str) -> bool:
        return name in self._items

    def add(self, item: NamedItem):
        if self._frozen:
            raise RuntimeError("Frozen instance")
        self._items[item.name] = item

    def all(self) -> Iterable[NamedItem]:
        yield from [s for s in self._items.values()]

    def filter(self, visibility: Visibility) -> Iterable[NamedItem]:
        """Filter item accoding visbility naming convention."""
        return filter(lambda s: match_visibility(name=s.name, visibility=visibility), self.all())

    def handler(self) -> RegisterHandler[NamedItem]:
        return self.add

    def freeze(self):
        self._frozen = True

    def frozen(self) -> bool:
        return self._frozen
