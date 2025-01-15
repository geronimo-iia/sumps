"""
String convert functions.


Original author: okunishinishi (Taka Okunishi)
from : https://github.com/okunishinishi/python-stringcase/blob/master/stringcase.py

Change:
 - naming syntax
 - typing
"""

import re

__all__ = [
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


def camel_case(name: str | None) -> str:
    """Convert name into camel case.

    Args:
        name: String to convert.

    Returns:
        name: Camel case name.

    """
    result = re.sub(r"^[\-_\.]+", "", str(name))
    if not result:
        return result
    return lower_case(result[0]) + re.sub(
        r"[\-_\.\s]([a-zA-Z])", lambda matched: upper_case(matched.group(1)), result[1:]
    )


def capital_case(name: str | None) -> str:
    """Convert name into capital case.
    First letters will be uppercase.

    Args:
        name: String to convert.

    Returns:
        name: Capital case name.

    """

    name = str(name)
    if not name:
        return name
    return upper_case(name[0]) + name[1:]


def const_case(name: str | None) -> str:
    """Convert name into upper snake case.
    Join punctuation with underscore and convert letters into uppercase.

    Args:
        name: String to convert.

    Returns:
        name: Const cased name.

    """

    return upper_case(snake_case(name))


def lower_case(name: str | None) -> str:
    """Convert name into lower case.

    Args:
        name: String to convert.

    Returns:
        name: Lowercase case name.

    """

    return str(name).lower()


def pascal_case(name: str | None) -> str:
    """Convert name into pascal case.

    Args:
        name: String to convert.

    Returns:
        name: Pascal case name.

    """

    return capital_case(camel_case(name))


def path_case(name: str | None) -> str:
    """Convert name into path case.
    Join punctuation with slash.

    Args:
        name: String to convert.

    Returns:
        name: Path cased name.

    """
    name = snake_case(name)
    if not name:
        return name
    return re.sub(r"_", "/", name)


def sentence_case(name: str | None) -> str:
    """Convert name into sentence case.
    First letter capped and each punctuations are joined with space.

    Args:
        name: String to convert.

    Returns:
        name: Sentence cased name.

    """
    joiner = " "
    name = re.sub(r"[\-_\.\s]", joiner, str(name))
    if not name:
        return name
    return capital_case(trim_case(re.sub(r"[A-Z]", lambda matched: joiner + lower_case(matched.group(0)), name)))


def snake_case(name: str | None) -> str:
    """Convert name into snake case.
    Join punctuation with underscore

    Args:
        name: String to convert.

    Returns:
        name: Snake cased name.

    """

    name = re.sub(r"[\-\.\s]", "_", str(name))
    if not name:
        return name
    return lower_case(name[0]) + re.sub(r"[A-Z]", lambda matched: "_" + lower_case(matched.group(0)), name[1:])


def spinal_case(name: str | None) -> str:
    """Convert name into spinal case.
    Join punctuation with hyphen.

    Args:
        name: String to convert.

    Returns:
        name: Spinal cased name.

    """

    return re.sub(r"_", "-", snake_case(name))


def dot_case(name: str | None) -> str:
    """Convert name into dot case.
    Join punctuation with dot.

    Args:
        name: String to convert.

    Returns:
        name: Dot cased name.

    """

    return re.sub(r"_", ".", snake_case(name))


def title_case(name: str | None) -> str:
    """Convert name into sentence case.
    First letter capped while each punctuations is capitalsed
    and joined with space.

    Args:
        name: String to convert.

    Returns:
        name: Title cased name.

    """

    return " ".join([capital_case(word) for word in snake_case(name).split("_")])


def trim_case(name: str | None) -> str:
    """Convert name into trimmed name.

    Args:
        name: String to convert.

    Returns:
        name: Trimmed case name
    """

    return str(name).strip()


def upper_case(name: str | None) -> str:
    """Convert name into upper case.

    Args:
        name: String to convert.

    Returns:
        name: Uppercase case name.

    """

    return str(name).upper()


def alphanum_case(name: str | None) -> str:
    """Cuts all non-alphanumeric symbols,
    i.e. cuts all expect except 0-9, a-z and A-Z.

    Args:
        name: String to convert.

    Returns:
        name: String with cutted non-alphanumeric symbols.

    """
    return "".join(filter(str.isalnum, str(name)))
