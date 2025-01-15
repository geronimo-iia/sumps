"""Langs declare few basic language elements."""

from .option import Nothing, Option, Some, maybe
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
from .types import get_builtin_type_names, qualified_name

__all__ = [
    # singleton
    "singleton",
    # option
    "maybe",
    "Option",
    "Some",
    "Nothing",
    # types
    "get_builtin_type_names",
    "qualified_name",
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
