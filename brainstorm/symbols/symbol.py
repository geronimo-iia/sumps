from __future__ import annotations

from typing import Any

from msgspec import Struct

from ..registry import Dictionary

__all__ = ["Symbol", "Symbols"]


class Symbol(Struct):
    name: str
    module: str | None = None
    annotation: str | type[Any] | None = None

    def __post_init__(self):
        if "." in self.name:
            raise RuntimeError(f"symbol {self.name} should not contains dot character.")

    @classmethod
    def from_qualified_name(cls, name: str) -> Symbol:
        index = name.rfind(".")
        if index < 0:
            return Symbol(name=name)
        return Symbol(name=name[index + 1 :], module=name[0:index])

    def qualified_name(self) -> str:
        return f"{self.module}.{self.name}"

    def __str__(self):
        return self.qualified_name()

    def __repr__(self):
        return f"{self.qualified_name()}: {self.annotation}" if self.annotation else self.qualified_name()


class Symbols(Dictionary[Symbol]):
    def group_per_module(self) -> dict[str, str]:
        grouped_dict = {}
        for symbol in self.all():
            if symbol.module not in grouped_dict:
                grouped_dict[symbol.module] = [symbol.name]
            else:
                grouped_dict[symbol.module].append(symbol.name)
        return grouped_dict
