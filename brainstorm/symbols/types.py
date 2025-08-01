import builtins
from functools import lru_cache

__all__ = ["get_builtin_type_names", "get_type_qualified_name"]


@lru_cache
def get_builtin_type_names() -> list[str]:
    """returns a list of builtin type name."""
    return [getattr(builtins, d).__name__ for d in dir(builtins) if isinstance(getattr(builtins, d), type)]


def get_type_qualified_name(o) -> str:
    """returns qualified named of a type."""
    klass = o.__class__
    module = klass.__module__
    if module == "builtins":
        return klass.__qualname__  # avoid outputs like 'builtins.str'
    return module + "." + klass.__qualname__
