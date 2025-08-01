import inspect
import uuid


class DynamicContext:
    """A dynamic namespace object to hold definitions from dynamic code."""
    def __init__(self, name=None):
        self.__name__ = name or f"context_{uuid.uuid4().hex}"

    def __repr__(self):
        return f"<DynamicContext {self.__name__}>"

def _get_caller_exports(include_private=False):
    """Extract caller symbols to inject."""
    frame = inspect.currentframe().f_back.f_back
    caller_globals = frame.f_globals
    return {
        k: v for k, v in caller_globals.items()
        if include_private or not k.startswith("_")
    }

def _generate_pyi_from_context(ctx: DynamicContext, stub_path: str):
    lines = [f"# Stub file for dynamic context '{ctx.__name__}'\n"]
    for name in dir(ctx):
        if name.startswith("_"):
            continue
        obj = getattr(ctx, name)
        if inspect.isfunction(obj):
            sig = inspect.signature(obj)
            doc = inspect.getdoc(obj)
            lines.append(f"def {name}{sig}:" + (f'  """{doc.splitlines()[0]}"""' if doc else " ..."))
            lines.append("")
        elif inspect.isclass(obj):
            doc = inspect.getdoc(obj)
            lines.append(f"class {name}:")
            lines.append(f"  \"\"\"{doc.splitlines()[0]}\"\"\"" if doc else "  pass")
            for mname, m in inspect.getmembers(obj):
                if mname.startswith("_") or not inspect.isfunction(m):
                    continue
                msig = inspect.signature(m)
                mdoc = inspect.getdoc(m)
                lines.append(f"  def {mname}{msig}:" + (f'  \"\"\"{mdoc.splitlines()[0]}\"\"\"' if mdoc else " ..."))
            lines.append("")
    with open(stub_path, "w") as f:
        f.write("\n".join(lines))

def load_dynamic_context(source: str, stub_path: str = None, include_private=False) -> DynamicContext:
    """
    Load code dynamically into a new DynamicContext object.
    Also injects caller's symbols and optionally generates a .pyi stub.
    """
    ctx = DynamicContext()
    ctx_dict = ctx.__dict__

    caller_exports = _get_caller_exports(include_private)
    exec(source, {**caller_exports, "ctx": ctx}, ctx_dict)

    if stub_path:
        _generate_pyi_from_context(ctx, stub_path)

    return ctx


# in the calling module
shared_var = 100

def helper(name):
    return f"Hello {name}, shared_var = {shared_var}"

code = '''
def foo():
    return helper("World")

class Greeter:
    """Example class."""
    def greet(self, who):
        return f"Greeting: {helper(who)}"

value = shared_var * 2
'''

ctx = load_dynamic_context(code, stub_path="ctx.pyi")

print(ctx.foo())               # Hello World, shared_var = 100
print(ctx.value)               # 200
print(ctx.Greeter().greet("Bob"))  # Greeting: Hello Bob, shared_var = 100