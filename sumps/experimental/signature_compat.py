# strudy on valiating signature composition of functions
from collections.abc import Callable
from inspect import Parameter, signature
from typing import Any


def get_first_param_type(fn: Callable) -> type | None:
    sig = signature(fn)
    params = list(sig.parameters.values())
    if not params:
        return None
    param = params[0]
    return None if param.annotation is Parameter.empty else param.annotation


def get_return_type(fn: Callable) -> type | None:
    return_annotation = signature(fn).return_annotation
    return None if return_annotation is Parameter.empty else return_annotation


def make_dummy(typ: type) -> Any:
    try:
        return typ()
    except Exception:
        if typ is int:
            return 0
        if typ is str:
            return ""
        if typ is float:
            return 0.0
        if typ is list:
            return []
        if typ is bool:
            return False
        return object()


def coerce_value(value: Any, target_type: type | None) -> Any:
    if target_type is None or isinstance(value, target_type):
        return value
    if target_type is bool:
        return bool(value)
    try:
        return target_type(value)
    except Exception as e:
        raise TypeError(f"Cannot coerce {value!r} to {target_type}") from e


def is_type_compatible(out_type: type, in_type: type) -> bool:
    try:
        if issubclass(out_type, in_type):
            return True
    except TypeError:
        pass
    try:
        dummy = make_dummy(out_type)
        coerce_value(dummy, in_type)
        return True
    except Exception:
        return False


def check_signature_composition(out_fn: Callable, in_fn: Callable, *, strict: bool = True) -> None:
    out_type = get_return_type(out_fn)
    in_type = get_first_param_type(in_fn)

    if in_type and out_type and not is_type_compatible(out_type, in_type):
        raise TypeError(f"Type mismatch: {out_type} -> {in_type} in function composition") from None

    if len(signature(in_fn).parameters) < 1:
        raise TypeError(f"{in_fn.__name__} expects no input, but a value is passed") from None
