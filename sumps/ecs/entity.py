"""
This module is heavly inspired from esper library.

esper is a lightweight Entity System (ECS) for Python, with a focus on performance
More information is available at https://github.com/benmoran56/esper

Here, i wanna explore this pattern using a manager class, msgspec for component, and see if
we could build archetype from scratch.
"""

from __future__ import annotations

from collections.abc import Iterable
from itertools import count as _count
from typing import TypeVar, overload

from msgspec import Struct

from sumps.lang import snake_case

__all__ = ["EntityId", "EntityDefinition", "component", "Component", "EntityManager", "Entity"]

type EntityId = int

type Component = Struct

C1 = TypeVar("C1", bound=Component)
C2 = TypeVar("C2", bound=Component)
C3 = TypeVar("C3", bound=Component)
C4 = TypeVar("C4", bound=Component)

type EntityDefinition = set[type[Component]]


def qualified_name(c: type[Component]) -> str:
    return snake_case(c.__name__)


def component(clzz: Struct):
    """Check, need to register ?"""
    return clzz


class Entity:
    id: EntityId

    def __init__(self, id: EntityId):
        self.id = id


class EntityHandler(Entity):
    manager: EntityManager

    def __init__(self, id: EntityId, manager: EntityManager):
        super().__init__(id=id)
        self.manager = manager

    def __getattr__(self, name):
        if self.id in self.manager._dead_entities:
            raise RuntimeError(f"Entity {self.id} is dead.")
        return self.manager._entities[self.id][name]


class EntityManager:
    _entity_count = _count(start=1)
    _entities: dict[EntityId, dict[str, Component]] = dict()
    _components: dict[str, set[EntityId]] = dict()
    _dead_entities: set[EntityId] = set()

    def create_entity(self, *components: Struct) -> EntityId:
        """Create a new Entity, with optional initial Components.

        This funcion returns an Entity ID, which is a plain integer.
        You can optionally pass one or more Component instances to be
        assigned to the Entity on creation. Components can be also be
        added later with the :py:func:`esper.add_component` funcion.
        """
        entity = next(self._entity_count)

        if entity not in self._entities:
            self._entities[entity] = {}

        for component_instance in components:
            component_type = qualified_name(type(component_instance))

            if component_type not in self._components:
                self._components[component_type] = set()

            self._components[component_type].add(entity)

            self._entities[entity][component_type] = component_instance

        return entity

    def get_entity(self, entity: EntityId) -> Entity:
        return EntityHandler(id=entity, manager=self)

    def delete_entity(self, entity: EntityId, immediate: bool = False) -> None:
        """Delete an Entity from the current World.

        Delete an Entity and all of it's assigned Component instances from
        the world. By default, Entity deletion is delayed until the next call
        to :py:func:`esper.process`. You can, however, request immediate
        deletion by passing the `immediate=True` parameter. Note that immediate
        deletion may cause issues, such as when done during Entity iteration
        (calls to esper.get_component/s).

        Raises a KeyError if the given entity does not exist in the database.
        """
        if immediate:
            for component_type in self._entities[entity]:
                self._components[component_type].discard(entity)

                if not self._components[component_type]:
                    del self._components[component_type]

            del self._entities[entity]

        else:
            self._dead_entities.add(entity)

    def entity_exists(self, entity: EntityId) -> bool:
        """Check if a specific Entity exists.

        Empty Entities (with no components) and dead Entities (destroyed
        by delete_entity) will not count as existent ones.
        """
        return entity in self._entities and entity not in self._dead_entities

    def component_for_entity(self, entity: EntityId, component_type: type[Component]) -> Component:
        """Retrieve a Component instance for a specific Entity.

        Retrieve a Component instance for a specific Entity. In some cases,
        it may be necessary to access a specific Component instance.
        For example: directly modifying a Component to handle user input.

        Raises a KeyError if the given Entity and Component do not exist.
        """
        return self._entities[entity][qualified_name(component_type)]

    def components_for_entity(self, entity: EntityId) -> tuple[Component, ...]:
        """Retrieve all Components for a specific Entity, as a Tuple.

        Retrieve all Components for a specific Entity. This function is probably
        not appropriate to use in your Processors, but might be useful for
        saving state, or passing specific Components between World contexts.
        Unlike most other functions, this returns all the Components as a
        Tuple in one batch, instead of returning a Generator for iteration.

        Raises a KeyError if the given entity does not exist in the database.
        """
        return tuple(self._entities[entity].values())

    def has_component(self, entity: EntityId, component_type: type[Component]) -> bool:
        """Check if an Entity has a specific Component type."""
        return qualified_name(component_type) in self._entities[entity]

    def has_components(self, entity: EntityId, *component_types: type[Component]) -> bool:
        """Check if an Entity has all the specified Component types."""
        components_dict = self._entities[entity]
        return all(comp_type in components_dict for comp_type in component_types)

    def add_component(
        self, entity: EntityId, component_instance: Component, type_alias: type[Component] | None = None
    ) -> None:
        """Add a new Component instance to an Entity.

        Add a Component instance to an Entiy. If a Component of the same type
        is already assigned to the Entity, it will be replaced.

        A `type_alias` can also be provided. This can be useful if you're using
        subclasses to organize your Components, but would like to query them
        later by some common parent type.
        """
        component_type = qualified_name(type_alias or type(component_instance))

        if component_type not in self._components:
            self._components[component_type] = set()

        self._components[component_type].add(entity)

        self._entities[entity][component_type] = component_instance

    def remove_component(self, entity: EntityId, component_type: type[Component]) -> Component:
        """Remove a Component instance from an Entity, by type.

        A Component instance can only be removed by providing its type.
        For example: esper.delete_component(enemy_a, Velocity) will remove
        the Velocity instance from the Entity enemy_a.

        Raises a KeyError if either the given entity or Component type does
        not exist in the database.
        """
        component_type_id = qualified_name(component_type)
        self._components[component_type_id].discard(entity)

        if not self._components[component_type_id]:
            del self._components[component_type_id]

        return self._entities[entity].pop(component_type_id)  # type: ignore[no-any-return]

    def get_component(self, component_type: type[Component]) -> Iterable[tuple[EntityId, Component]]:
        """Get an iterator for Entity, Component pairs."""
        entity_db = self._entities

        component_type_id = qualified_name(component_type)

        for entity in self._components.get(component_type_id, []):
            yield entity, entity_db[entity][component_type_id]

    @overload
    def get_components(self, c1: type[C1]) -> Iterable[tuple[EntityId, tuple[C1]]]: ...

    @overload
    def get_components(self, c1: type[C1], c2: type[C2]) -> Iterable[tuple[EntityId, tuple[C1, C2]]]: ...

    @overload
    def get_components(
        self, c1: type[C1], c2: type[C2], c3: type[C3]
    ) -> Iterable[tuple[EntityId, tuple[C1, C2, C3]]]: ...

    @overload
    def get_components(
        self, c1: type[C1], c2: type[C2], c3: type[C3], c4: type[C4]
    ) -> Iterable[tuple[EntityId, tuple[C1, C2, C3, C4]]]: ...

    def get_components(self, *component_types: type[Component]) -> Iterable[tuple[EntityId, tuple[Component, ...]]]:  # type: ignore
        entity_db = self._entities
        comp_db = self._components

        component_type_ids = [qualified_name(ct) for ct in component_types]

        try:
            for entity in set.intersection(*[comp_db[ct] for ct in component_type_ids]):
                yield entity, tuple(entity_db[entity][ct] for ct in component_type_ids)
        except KeyError:
            pass

    def try_component(self, entity: EntityId, component_type: type[Component]) -> Component | None:
        """Try to get a single component type for an Entity.

        This function will return the requested Component if it exists,
        or None if it does not. This allows a way to access optional Components
        that may or may not exist, without having to first query if the Entity
        has the Component type.
        """
        if component_type in self._entities[entity]:
            return self._entities[entity][component_type]
        return None

    @overload
    def try_components(self, entity: EntityId, c1: type[C1]) -> tuple[C1] | None: ...

    @overload
    def try_components(self, entity: EntityId, c1: type[C1], c2: type[C2]) -> tuple[C1, C2] | None: ...

    @overload
    def try_components(
        self, entity: EntityId, c1: type[C1], c2: type[C2], c3: type[C3]
    ) -> tuple[C1, C2, C3] | None: ...

    @overload
    def try_components(
        self, entity: EntityId, c1: type[C1], c2: type[C2], c3: type[C3], c4: type[C4]
    ) -> tuple[C1, C2, C3, C4] | None: ...

    def try_components(self, entity: EntityId, *component_types: type[Component]) -> tuple[Component, ...] | None:  # type: ignore
        """Try to get a multiple component types for an Entity.

        This function will return the requested Components if they exist,
        or None if they do not. This allows a way to access optional Components
        that may or may not exist, without first having to query if the Entity
        has the Component types.
        """
        if all(comp_type in self._entities[entity] for comp_type in component_types):
            return tuple(self._entities[entity][qualified_name(comp_type)] for comp_type in component_types)
        return None

    def clear_dead_entities(self) -> None:
        """Finalize deletion of any Entities that are marked as dead.

        This function is provided for those who are not making use of
        :py:func:`esper.add_processor` and :py:func:`esper.process`. If you are
        calling your processors manually, this function should be called in
        your main loop after calling all processors.
        """
        for entity in self._dead_entities:
            self.delete_entity(entity=entity, immediate=True)

        self._dead_entities.clear()
