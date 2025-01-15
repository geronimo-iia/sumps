"""Compose implements function composition."""

from asyncio import iscoroutinefunction
from collections.abc import Callable
from inspect import signature

from sumps.aio.wrapper import async_wrapper
from sumps.lang.symbols import FunctionStatement, Module

from .identity import identity

__all__ = ["compose", "pipe"]


class Compose:
    """Compose function calls and compile the resulting function."""

    def __init__(self, funcs):
        funcs = tuple(reversed(funcs))
        self.first = funcs[0]
        self.funcs = funcs[1:]

    def __hash__(self):
        return hash(self.first) ^ hash(self.funcs)

    def __signature__(self):
        base = signature(self.first)
        last = signature(self.funcs[-1])
        return base.replace(return_annotation=last.return_annotation)

    def __repr__(self):
        return str(self.__signature__())

    def __eq__(self, other):
        if isinstance(other, Compose):
            return other.first == self.first and other.funcs == self.funcs
        return NotImplemented

    def __call__(self, *args, **kwargs):
        ret = self.first(*args, **kwargs)
        for f in self.funcs:
            ret = f(ret)
        return ret

    def compile(self) -> Callable:
        """Compile compose expression."""

        _locals = {}
        # we cant use specification.add_symbol due to local function definition (inner function instance)
        # module.specification.add_symbol(qualified_name= qualified_function_name( self.first))
        _locals[self.first.__name__] = self.first
        for f in self.funcs:
            # module.specification.add_symbol(qualified_name=qualified_function_name(f ))
            _locals[f.__name__] = f

        is_async = isinstance(self, AsyncCompose)
        function = FunctionStatement(name="compose", is_async=is_async)
        function.set_signature(self.__signature__())

        pre_call = "await " if is_async else ""
        body = (
            f"{pre_call}{self.first.__name__}("
            + ", ".join([f"{param.name} = {param.name}" for param in signature(self.first).parameters.values()])
            + ")"
        )
        for f in self.funcs:
            param = next(iter(signature(f).parameters.values()))
            body = f"{pre_call}{f.__name__}({param.name} = {body})"
        body = f"\treturn {body}"

        function.body = body

        return function.register(module=Module(name="composer")).import_module(locals=_locals)[function.name]


class AsyncCompose(Compose):
    def __init__(self, funcs):
        super().__init__(funcs=[async_wrapper(f) for f in funcs])

    async def __call__(self, *args, **kwargs):
        ret = await self.first(*args, **kwargs)
        for f in self.funcs:
            ret = await f(ret)
        return ret

    def __eq__(self, other):
        if isinstance(other, AsyncCompose):
            return other.first == self.first and other.funcs == self.funcs
        return NotImplemented


def compose(*funcs):
    """
    Compose functions (async or sync) to operate in series.
    Returns a function that applies other functions in sequence.

    Functions are applied from right to left so that
    ``compose(f, g, h)(x, y)`` is the same as ``f(g(h(x, y)))``.

    If no arguments are provided, the identity function (f(x) = x) is returned.
    """
    if not funcs:
        return identity
    if len(funcs) == 1:
        return funcs[0]
    else:
        if any([iscoroutinefunction(f) for f in funcs]):
            return AsyncCompose(funcs).compile()
        return Compose(funcs).compile()


def pipe(*funcs):
    """
    Pipe functions (async or sync) to operate in series.

    ``pipe(f, g, h)(data)`` is equivalent to ``h(g(f(data)))``

    If no arguments are provided, the identity function (f(x) = x) is returned.
    """
    return compose(*reversed(funcs))
