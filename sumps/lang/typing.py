from __future__ import annotations

from typing import Any

from msgspec import Struct

from .stringcase import pascal_case, snake_case
from .symbols import Module, Statement

__all__ = ["Intersection", "Archetype"]


def Intersection(parameters: list[type[Any]], name: str | None = None) -> type[Any]:
    """Intersection type; Intersection[X, Y] means either X and Y.


    To define an intersection, use e.g. Intersection[A, B]. Details:
    - The arguments must be types and there must be at least one.
    - Intersections of a single argument vanish, e.g.::

        assert Intersection[int] == int  # The constructor actually returns int

    - Redundant arguments are skipped, e.g.::

        assert Intersection[A, B, A] == Intersection[A, B]

    """
    if type(None) in parameters:
        raise TypeError("Cannot take a Intersection of 'None' types.")

    for p in parameters:
        if p.__module__ == "builtins":
            raise TypeError("Cannot take a Intersection of builtins types.")

    if len(parameters) == 1:
        return parameters[0]

    parameters = _deduplicate(parameters)
    m = Module(name="intersection")
    for p in parameters:
        m.add_class_reference(p)

    p_names = [p.__qualname__ for p in parameters]
    name = name if name else "".join(p_names)
    m.statements.add(item=Statement(name=name, body=f"class {name}({', '.join(p_names)}):\n\tpass\n"))
    return m.import_module()[name]


def Archetype(
    name: str, attributs: list[type[Any]], parents: list[type[Any]] | None = None, options: dict[str, Any] | None = None
) -> type[Any]:
    # TODO add optional attributs, support for type expression and default factory (field)
    parents = parents if parents else list()

    name = pascal_case(name)

    has_struct = False
    for p in parents:
        if issubclass(p, Struct):
            has_struct = True
        if p.__module__ == "builtins":
            raise TypeError("Cannot take a builtins types as parent.")
    if not has_struct:
        parents.append(Struct)

    attributs = _deduplicate(attributs)

    m = Module(name="archetype")

    for p in parents:
        m.add_class_reference(p)

    p_names = [p.__qualname__ for p in parents]
    if options:
        for k, v in options.items():
            p_names.append(f"{k}={str(v)}")

    body = [f"class {name}({', '.join(p_names)}):"]

    for attribut in attributs:
        m.add_class_reference(attribut)
        body.append(f"\t{snake_case(attribut.__name__)}:{attribut.__qualname__}")

    m.statements.add(item=Statement(name=name, body="\n".join(body)))

    return m.import_module()[name]


def _deduplicate(params):
    # Weed out strict duplicates, preserving the first of each occurrence.
    all_params = set(params)
    if len(all_params) < len(params):
        new_params = []
        for t in params:
            if t in all_params:
                new_params.append(t)
                all_params.remove(t)
        params = new_params
        assert not all_params, all_params
    return params
