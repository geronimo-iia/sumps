"""Compose implements function composition."""

# Import necessary modules for function composition
from collections.abc import Callable
from inspect import Signature, signature
from typing import Any

from sumps.aio import ensure_async, iscoroutinefunction
from sumps.lang.module_builder import FunctionSymbol, ModuleBuilder

from .identity import identity

__all__ = ["compose", "pipe"]


class Compose:
    """
    Compose function calls and compile the resulting function.

    Handles synchronous function composition with dynamic code generation.

    Support lambda function composition.
    """

    def __init__(self, funcs: tuple[Callable[..., Any], ...]):
        """Initialize composition with list of functions."""
        if not funcs:
            raise ValueError("At least one function must be provided")

        # Reverse functions to apply left to right in composition
        _funcs = tuple(reversed(funcs))
        self.first = _funcs[0]  # First function to call
        self.funcs = _funcs[1:]  # Remaining functions in chain
        self._cached_signature: Signature | None = None  # Cache for signature

    def __hash__(self):
        """Hash based on composed functions."""
        return hash(self.first) ^ hash(self.funcs)

    def __signature__(self) -> Signature:
        """Get signature combining first function's params with last function's return type."""
        if self._cached_signature is None:
            base = signature(self.first)  # Parameters from first function
            last = signature(self.funcs[-1])  # Return type from last function
            self._cached_signature = base.replace(return_annotation=last.return_annotation)
        return self._cached_signature

    def __repr__(self):
        """String representation showing the composed signature."""
        return str(self.__signature__())

    def __eq__(self, other):
        """Equality based on composed functions."""
        if isinstance(other, Compose):
            return other.first == self.first and other.funcs == self.funcs
        return NotImplemented

    def __call__(self, *args, **kwargs) -> Any:
        """Execute the composed functions in sequence."""
        # Call first function with original arguments
        ret = self.first(*args, **kwargs)
        # Chain remaining functions, passing result through each
        for f in self.funcs:
            ret = f(ret)
        return ret

    def build(self) -> Callable:
        """Compile compose expression into optimized dynamic function."""
        # Create module builder for dynamic code generation
        mod = ModuleBuilder(name="composer")

        # Add functions to local symbol table (can't use global due to closures)

        mod.locals.add_function(func=self.first, support_lambda=True)
        for f in self.funcs:
            mod.locals.add_function(func=f, ignore_duplicate=True, support_lambda=True)

        # Create function symbol with proper signature
        function = FunctionSymbol.from_signature(name="compose", signature=self.__signature__(), is_async=isinstance(self, AsyncCompose))

        # Generate function body with proper async/sync calls
        pre_call = "await " if function.is_async else ""

        # Build initial function call with all parameters
        body = (
            f"{pre_call}{self.first.__name__}("
            + ", ".join([f"{param.name} = {param.name}" for param in signature(self.first).parameters.values()])
            + ")"
        )

        # Chain remaining function calls
        for f in self.funcs:
            param = next(iter(signature(f).parameters.values()))
            body = f"{pre_call}{f.__name__}({param.name} = {body})"

        # Complete function body with return statement
        body = f"\treturn {body}"
        function.body = body
        mod.add_statement(function)

        # Build and return the compiled function
        return mod.build().get_reference_function(name=function.name, weak=False)


class AsyncCompose(Compose):
    """Async version of Compose for coroutine function composition."""

    def __init__(self, funcs: tuple[Callable[..., Any], ...]):
        """Initialize with async-wrapped functions."""
        # Ensure all functions are async-compatible
        super().__init__(tuple(ensure_async(f) for f in funcs))

    async def __call__(self, *args, **kwargs):
        """Execute the composed async functions in sequence."""
        # Await first function with original arguments
        ret = await self.first(*args, **kwargs)
        # Chain remaining async functions
        for f in self.funcs:
            ret = await f(ret)
        return ret

    def __eq__(self, other):
        """Equality for async compose instances."""
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
    # Return identity for no functions
    if not funcs:
        return identity
    # Return single function as-is
    if len(funcs) == 1:
        return funcs[0]
    else:
        # Choose async or sync composition based on function types
        if any([iscoroutinefunction(f) for f in funcs]):
            return AsyncCompose(funcs).build()
        return Compose(funcs).build()


def pipe(*funcs):
    """
    Pipe functions (async or sync) to operate in series.

    ``pipe(f, g, h)(data)`` is equivalent to ``h(g(f(data)))``

    If no arguments are provided, the identity function (f(x) = x) is returned.
    """
    # Reverse function order to convert pipe to compose
    return compose(*reversed(funcs))
