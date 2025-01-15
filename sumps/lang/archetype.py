from __future__ import annotations

from collections.abc import Callable
from typing import Any, Literal, TypeVar

from msgspec import UNSET, Struct, UnsetType, field
from msgspec.structs import asdict

from .factory import factory
from .stringcase import pascal_case, snake_case
from .symbols import Dictionary, Module, Statement, Symbol

T = TypeVar("T", bound=Struct)


__all__ = ["Rename", "Property", "Archetype", "component"]

type Rename = Literal["lower", "upper", "camel", "pascal", "kebab"]


def component(clzz: Struct):
    return clzz


class ArchetypeOptions(Struct):
    kw_only: bool = False
    tag: bool = False
    tag_name: str | None = None
    rename: Rename | None = None
    array_like: bool = False
    gc: bool = True
    weakref: bool = False
    dict: bool = False
    cache_hash: bool = False
    omit_defaults: bool = False
    repr_omit_defaults: bool = False
    forbid_unknown_fields: bool = False
    frozen: bool = False
    eq: bool = True
    order: bool = False


class Property(Symbol, kw_only=True):
    cls: type[Any]  # or Type[Struct]
    optional: bool = False
    default: int | bool | str | float | Struct | UnsetType = UNSET
    default_factory: Callable[[], Any] | None = None

    def _post_init(self):
        if self.default != UNSET and self.default_factory:
            raise RuntimeError("Could not set default and default_factory in the same property definition.")


class Archetype(Statement, kw_only=True):
    _parents: list[type[Any]] = field(default_factory=list)
    _properties: Dictionary[Property] = field(default_factory=factory(Dictionary[Property]))
    options: ArchetypeOptions = ArchetypeOptions()

    def __post_init__(self):
        self.name = pascal_case(self.name)
        return super().__post_init__()

    def add_parent(self, cls: type[Any]) -> Archetype:
        if self._properties.frozen():
            raise RuntimeError("This archetype is ever registered (you could not change it)")
        self._parents.append(cls)
        return self

    def add_property(
        self,
        cls: type[Any],
        name: str | None = None,
        optional: bool = False,
        default: int | bool | str | float | Struct | UnsetType = UNSET,
        default_factory: Callable[[], Any] | None = None,
    ) -> Archetype:
        name = name if name else snake_case(cls.__name__)
        self._properties.add(
            item=Property(name=name, cls=cls, optional=optional, default=default, default_factory=default_factory)
        )

        return self

    def _get_parents(self) -> list[type[Any]]:
        parents = self._parents
        has_struct = False
        for p in parents:
            if issubclass(p, Struct):
                has_struct = True
            if p.__module__ == "builtins":
                raise TypeError("Cannot take a builtins types as parent.")
        if not has_struct:
            parents.append(Struct)
        return parents

    def register(self, module: Module) -> Module:
        """Should be call if definition change."""
        module = super().register(module=module)

        parents = self._get_parents()

        for p in parents:
            module.add_class_reference(p)

        p_names = [p.__qualname__ for p in parents]
        if self.options:
            for k, v in asdict(self.options).items():
                p_names.append(f"{k}={str(v)}")

        name = pascal_case(self.name)
        body = [f"class {name}({', '.join(p_names)}):"]

        need_field = False
        for property in self._properties.all():
            # could be more complexe
            module.add_class_reference(property.cls)

            declaration = f"\t{snake_case(property.name)}:{property.cls.__qualname__}"
            if property.default != UNSET:
                need_field = True
                declaration += f" = field(default_factory=lambda: {property.default})"
            if property.default_factory:
                need_field = True
                # import function
                declaration += f" = field(default_factory={property.default_factory})"
            body.append(declaration)

            need_field = property.default_factory is not None

        if need_field:
            module.specification.add_symbol(qualified_name="msgspec.field")

        self.body = "\n".join(body)

        self._properties.freeze()

        return module
