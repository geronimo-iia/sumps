import inspect
import os
import types
from io import TextIOBase


def get_calling_frame():
    return inspect.currentframe().f_back # type: ignore

def get_calling_module():
    return inspect.getmodule(get_calling_frame()) # type: ignore

def get_calling_module_info() -> tuple[str, str|None]:
    mod = get_calling_module()
    if not mod or not hasattr(mod, '__file__'):
        raise RuntimeError("Could not resolve calling module")
    return  mod.__name__, os.path.abspath(mod.__file__) # type: ignore


def generate_importer_module(suffix: str="generated") -> str:
    module_name, module_file = get_calling_module_info()

    # Ensure the module is importable (adjust if needed)
    if module_name == "__main__" or module_file is None:
        raise RuntimeError("Cannot generate importer for main module or modules without a file path")

    output_path = module_file.replace(".py", f"_{suffix}.py")
    with open(output_path, "w") as f:
        f.write(f"""# Auto-generated module
import {module_name}
""")
    return output_path

import traceback
from typing import Literal

type TargetMode = Literal["expression", "statements"]

def run_in_caller(code_str: str, mode: TargetMode = "expression"):
    """
    Compile and run code_str in the caller's module context.

    Args:
        code_str: The Python source code (expression or statements).
        mode: 'eval' for expressions, 'exec' for statements.

    Returns:
        The result of eval() if mode='eval', else None.
    
    Raises:
        SyntaxError, NameError, etc. if code fails to compile or run.
    """
    caller_frame = inspect.currentframe().f_back
    caller_globals = caller_frame.f_globals
    caller_locals = caller_frame.f_locals

    compile_mode = "eval" if mode == "expression" else "exec"
    try:
        code = compile(code_str, "<dynamic>", compile_mode)
        
            
        if mode == "expression":
            return eval(code, caller_globals, caller_locals)
        elif mode == "statements":
            exec(code, caller_globals, caller_locals)
        else:
            raise ValueError(f"Unsupported mode: {mode}")
    except Exception:
        tb = traceback.format_exc()
        print(f"Error running code in caller context:\n{tb}")
        raise

def run_statements_and_return(code_str: str):
    caller_frame = inspect.currentframe().f_back
    caller_globals = caller_frame.f_globals
    caller_locals = caller_frame.f_locals.copy()  # copy to avoid mutation

    # Wrap user code in a function to return results
    func_code = f"""
def __temp_func():
{chr(10).join('    ' + line for line in code_str.splitlines())}
    return locals()
"""

    exec(func_code, caller_globals, caller_locals)
    result_locals = caller_globals['__temp_func']()
    del caller_globals['__temp_func']

    return result_locals


def eval_in_caller(expr: str, mode:str = "eval"):
    """Compile and evaluate a Python expression dynamically in the context (namespace) of the calling module."""

    #Use mode='eval' for expressions, mode='exec' if you want statements (e.g. function defs)
    #You can also do exec(code, caller_globals, caller_locals) if the code is a statement or block

    # Get the caller's frame (one step up the call stack)
    caller_frame = inspect.currentframe().f_back
    # Extract globals and locals from caller's frame
    caller_globals = caller_frame.f_globals
    caller_locals = caller_frame.f_locals

    # Compile the expression (eval mode)
    code = compile(expr, filename="<string>", mode=mode)

    # Evaluate the expression with caller's namespaces
    return eval(code, caller_globals, caller_locals)

def export_references_to(output: TextIOBase):
    frame = get_calling_frame()
    caller_globals = frame.f_globals # type: ignore
    caller_module = inspect.getmodule(frame)
    del frame  # avoid reference cycles

    module_name = caller_module.__name__ # type: ignore

    # Collect importable symbols
    symbols = []
    # Only export user-defined symbols (not builtins or imports)
    for name, value in caller_globals.items():
        if name.startswith("__"):
            continue
        if isinstance(value, (types.FunctionType, type, int, float, str, list, dict, set)):
            symbols.append(name)

    # Generate the output
    lines = [
        f"# Auto-generated from {module_name}",
        f"from {module_name} import {', '.join(symbols)}",
        "",
    ]

    output.write("\n".join(lines))

    return output


def merge_modules(src_module, dest_module):
    """Merge Definitions Between Modules.
    
    This allows us to dynamically inherit or patch modules.
    """
    for name in dir(src_module):
        if name.startswith("__"): continue
        setattr(dest_module, name, getattr(src_module, name))


def inject_into_caller(symbols: dict):
    frame = get_calling_frame()
    caller_globals = frame.f_globals # type: ignore
    del frame  # avoid leaks

    for name, obj in symbols.items():
        caller_globals[name] = obj

#runpy.run_path("generated_importer.py")

def analyze_current_module():
    """analyze the module from which it's called."""
    module =get_calling_module()
    # avoid memory leaks due to lingering frame references
    if module is None:
        raise RuntimeError("Could not determine calling module")
    return analyze_module(module)


def analyze_module(mod):
    info = {
        "name": mod.__name__,
        "doc": inspect.getdoc(mod),
        "functions": [],
        "classes": []
    }

    for name, obj in inspect.getmembers(mod):
        if inspect.isfunction(obj) and obj.__module__ == mod.__name__:
            info["functions"].append({
                "name": name,
                "args": list(inspect.signature(obj).parameters.keys()),
                "doc": inspect.getdoc(obj)
            })
        elif inspect.isclass(obj) and obj.__module__ == mod.__name__:
            methods = []
            for meth_name, meth in inspect.getmembers(obj, inspect.isfunction):
                if meth.__module__ == mod.__name__:
                    methods.append({
                        "name": meth_name,
                        "args": list(inspect.signature(meth).parameters.keys()),
                        "doc": inspect.getdoc(meth)
                    })
            info["classes"].append({
                "name": name,
                "doc": inspect.getdoc(obj),
                "methods": methods
            })

    return info
