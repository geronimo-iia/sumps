"""Langs declare few basic language elements."""

from .option import Nothing, Option, Some, just, maybe
from .singleton import singleton
from .stringcase import (
    alphanum_case,
    camel_case,
    capital_case,
    const_case,
    dot_case,
    lower_case,
    pascal_case,
    path_case,
    sentence_case,
    snake_case,
    spinal_case,
    title_case,
    trim_case,
    upper_case,
)

# from .symbols.types import get_builtin_type_names, get_type_qualified_name
from .typing import Intersection

__all__ = [
    # singleton
    "singleton",
    # option
    "maybe",
    "just",
    "Option",
    "Some",
    "Nothing",
    # typing
    "Intersection",
    # stringcase
    "camel_case",
    "capital_case",
    "const_case",
    "lower_case",
    "pascal_case",
    "path_case",
    "sentence_case",
    "snake_case",
    "spinal_case",
    "dot_case",
    "title_case",
    "trim_case",
    "upper_case",
    "alphanum_case",
]
