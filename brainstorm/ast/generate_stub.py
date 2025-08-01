import inspect
import os
import types
from typing import Any


def get_doc_summary(obj: Any) -> str:
    doc = inspect.getdoc(obj)
    if doc:
        return doc.strip().split("\n")[0]
    return ""


def format_arg(arg):
    if arg.annotation is inspect.Parameter.empty:
        return arg.name
    return f"{arg.name}: {arg.annotation.__name__ if hasattr(arg.annotation, '__name__') else 'Any'}"

def format_signature(sig: inspect.Signature) -> str:
    params = list(sig.parameters.values())
    formatted = [format_arg(p) for p in params]
    return f"({', '.join(formatted)})"

def generate_stub(module: types.ModuleType, output_path: str) -> None:
    """Generates .pyi stubs from a live Python module

    Adds one-line docstring summaries as comments above each symbol
    Supports:
        Top-level functions
        Classes and their methods
        Simple constants (int, float, str, bool)
    Falls back to Any if no type info is available
    
    """
    lines = ["from typing import Any\n"] # Defaults to Any if no type hint is available.

    for name, obj in vars(module).items():
        if name.startswith("_"):
            continue

        doc = get_doc_summary(obj)

        # Constants
        if isinstance(obj, (int, float, str, bool)):
            if doc:
                lines.append(f"# {doc}")
            lines.append(f"{name}: {type(obj).__name__}")
            continue

        # Functions
        if inspect.isfunction(obj) and obj.__module__ == module.__name__:
            if doc:
                lines.append(f"# {doc}")
            try:
                sig = inspect.signature(obj)
                return_type = sig.return_annotation
                return_str = (
                    return_type.__name__
                    if return_type is not inspect.Signature.empty and hasattr(return_type, "__name__")
                    else "Any"
                )
                args_str = format_signature(sig)
                lines.append(f"def {name}{args_str} -> {return_str}: ...")
            except Exception:
                lines.append(f"def {name}(*args: Any, **kwargs: Any) -> Any: ...")
            continue

        # Classes
        if inspect.isclass(obj) and obj.__module__ == module.__name__:
            if doc:
                lines.append(f"# {doc}")
            lines.append(f"\nclass {name}:")
            methods = inspect.getmembers(obj, predicate=inspect.isfunction)
            if not methods:
                lines.append("    ...")
            for m_name, method in methods:
                if m_name.startswith("_") and m_name != "__init__":
                    continue
                mdoc = get_doc_summary(method)
                try:
                    sig = inspect.signature(method)
                    args_str = format_signature(sig)
                    return_type = sig.return_annotation
                    return_str = (
                        return_type.__name__
                        if return_type is not inspect.Signature.empty and hasattr(return_type, "__name__")
                        else "Any"
                    )
                    if mdoc:
                        lines.append(f"    # {mdoc}")
                    lines.append(f"    def {m_name}{args_str} -> {return_str}: ...")
                except Exception:
                    lines.append(f"    def {m_name}(self, *args: Any, **kwargs: Any) -> Any: ...")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write("\n".join(lines))
