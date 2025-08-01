import inspect
import json
import os
import types
from typing import Any


def get_doc_summary(obj: Any) -> str:
    doc = inspect.getdoc(obj)
    return doc.strip().split("\n")[0] if doc else ""

def format_arg(arg):
    if arg.annotation is inspect.Parameter.empty:
        return arg.name
    ann = arg.annotation
    return f"{arg.name}: {ann.__name__ if hasattr(ann, '__name__') else 'Any'}"

def format_signature(sig: inspect.Signature) -> str:
    params = list(sig.parameters.values())
    formatted = [format_arg(p) for p in params]
    return f"({', '.join(formatted)})"

def generate_stub_with_docs_and_json(
    module: types.ModuleType,
    pyi_path: str,
    json_path: str,
    include_private: bool = False
) -> None:
    lines = ["from typing import Any\n"]
    json_doc = {
        "module": module.__name__,
        "constants": [],
        "functions": [],
        "classes": [],
    }

    for name, obj in vars(module).items():
        if not include_private and name.startswith("_"):
            continue
        if name in ("__builtins__", "__doc__", "__file__", "__name__", "__package__", "__loader__"):
            continue

        doc = get_doc_summary(obj)

        # Constants
        if isinstance(obj, (int, float, str, bool)):
            if doc:
                lines.append(f"# {doc}")
            lines.append(f"{name}: {type(obj).__name__}")
            json_doc["constants"].append({
                "name": name,
                "type": type(obj).__name__,
                "doc": doc
            })
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
                json_doc["functions"].append({
                    "name": name,
                    "args": [format_arg(p) for p in sig.parameters.values()],
                    "return": return_str,
                    "doc": doc
                })
            except Exception:
                lines.append(f"def {name}(*args: Any, **kwargs: Any) -> Any: ...")
                json_doc["functions"].append({
                    "name": name,
                    "args": ["*args", "**kwargs"],
                    "return": "Any",
                    "doc": doc
                })
            continue

        # Classes
        if inspect.isclass(obj) and obj.__module__ == module.__name__:
            if doc:
                lines.append(f"# {doc}")
            lines.append(f"\nclass {name}:")
            class_info = {
                "name": name,
                "doc": doc,
                "methods": []
            }
            methods = inspect.getmembers(obj, predicate=inspect.isfunction)
            if not methods:
                lines.append("    ...")
            for m_name, method in methods:
                if not include_private and m_name.startswith("_") and m_name != "__init__":
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
                    class_info["methods"].append({
                        "name": m_name,
                        "args": [format_arg(p) for p in sig.parameters.values()],
                        "return": return_str,
                        "doc": mdoc
                    })
                except Exception:
                    lines.append(f"    def {m_name}(self, *args: Any, **kwargs: Any) -> Any: ...")
                    class_info["methods"].append({
                        "name": m_name,
                        "args": ["*args", "**kwargs"],
                        "return": "Any",
                        "doc": mdoc
                    })

            json_doc["classes"].append(class_info)

    os.makedirs(os.path.dirname(pyi_path), exist_ok=True)
    with open(pyi_path, "w") as f:
        f.write("\n".join(lines))

    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    with open(json_path, "w") as f:
        json.dump(json_doc, f, indent=2)
