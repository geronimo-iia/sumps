from __future__ import annotations

from typing import Any

from .module_builder import ClassSymbol, ModuleBuilder

__all__ = ["Intersection"]


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
    m = ModuleBuilder(name="intersection")
    for p in parameters: # use locals instead of reference to support dynmaic classes
        m.locals.add_class(p)

    p_names = [p.__qualname__ for p in parameters]
    name = name if name else "".join(p_names)
    m.add_statement(stmt=ClassSymbol(name=name, bases=p_names, body="pass\n"))
    try:
        return m.build().get_reference(name=name)
    except RuntimeError as r:
        raise TypeError(r) from r


