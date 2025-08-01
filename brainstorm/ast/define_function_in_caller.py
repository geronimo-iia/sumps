import inspect
import textwrap
from types import FunctionType


def define_function_in_caller(name: str, signature: str, body: str, doc: str = "") -> FunctionType:
    """
    Define and return a new function dynamically in the caller's global scope.

    Args:
        name: Name of the function to define.
        signature: Function parameters as a string (e.g., "x, y=0").
        body: The function body as a string (supports multiline).
        doc: Optional function docstring.

    Returns:
        The defined function object (also injected into caller's globals).
    """
    caller_frame = inspect.currentframe().f_back
    caller_globals = caller_frame.f_globals

    doc_line = f'    """{doc}"""\n' if doc else ""
    body_block = textwrap.indent(textwrap.dedent(body), "    ")

    source = f"def {name}({signature}):\n{doc_line}{body_block}\n"

    # Temporary local namespace to extract function object
    local_namespace = {}
    exec(source, caller_globals, local_namespace)

    # Inject into caller globals explicitly
    func = local_namespace[name]
    caller_globals[name] = func
    return func


f = define_function_in_caller(
    name="triple",
    signature="x",
    body="return x * 3",
    doc="Returns x multiplied by 3."
)

print(triple(10))  # 30 — available in caller scope
print(f(5))        # 15 — same function as `triple`
print(f.__doc__)   # Returns x multiplied by 3.
