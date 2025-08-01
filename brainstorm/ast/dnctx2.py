import inspect
import textwrap
import uuid


class ReloadableDynamicContext:
    def __init__(self, name: str | None = None, source: str | None = None, include_private: bool = False):
        self.__name__ = name or f"context_{uuid.uuid4().hex}"
        self.__dict__["__source__"] = source
        self.__dict__["__include_private__"] = include_private
        self.__dict__["__caller_globals__"] = self._capture_caller_globals(include_private)

        if source:
            self.update(source)

    def __repr__(self):
        return f"<ReloadableDynamicContext {self.__name__}>"

    def _capture_caller_globals(self, include_private=False):
        frame = inspect.currentframe().f_back.f_back  # 2 levels up from here
        caller_globals = frame.f_globals
        caller_locals = frame.f_locals

        result = {
            k: v for k, v in caller_globals.items()
            if include_private or not k.startswith("_")
        }

        for k, v in caller_locals.items():
            result[k]=v
        
        return result

    def update(self, source: str, stub_path: str | None = None):
        """
        Recompile and reload new source into the same context.
        """
        self.__dict__["__source__"] = source
        exec(
            textwrap.dedent(source),
            {**self.__dict__["__caller_globals__"], "ctx": self},
            self.__dict__,
        )
        if stub_path:
            self._generate_pyi_stub(stub_path)

    def _generate_pyi_stub(self, stub_path: str):
        lines = [f"# Stub file for dynamic context '{self.__name__}'\n"]
        for name in dir(self):
            if name.startswith("_"):
                continue
            obj = getattr(self, name)
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


shared_value = 42

def helper(name): return f"[{name.upper()}] = {shared_value}"

ctx = ReloadableDynamicContext(include_private=True)

ctx.update("""
def show():
    return helper("reload")
val = shared_value * 2
""", stub_path="ctx.pyi")

print(ctx.show())     # [RELOAD] = 42
print(ctx.val)        # 84

# Later, you recompile with new logic
ctx.update("""
def show():
    return "UPDATED: " + helper("again")
val = shared_value + 1
""")

print(ctx.show())  # UPDATED: [AGAIN] = 42
print(ctx.val)     # 43



def add(a: int, b: int) -> int:
    return a + b


def double(a: int) -> int:
    return a * a

ctx.update("""
def show(a, b):
    return double(add(a, b))
""")

print(ctx.show(1, 2))
print(ctx.show(2, 2))