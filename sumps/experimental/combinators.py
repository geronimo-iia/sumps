"""Combinators."""

from collections.abc import Callable

from sumps.func import compose


def apply(a: Callable, b: Callable) -> Callable:
    return compose(a, b)


def bluebird(a: Callable, b: Callable, c: Callable) -> Callable:
    return compose(a, b, c)


def blackbird(a: Callable, b: Callable, c: Callable, d: Callable) -> Callable:
    #return a(b(c)(d))
    return compose(a, compose(compose(b, c), d))

def cardinal(a: Callable, b: Callable, c: Callable) -> Callable:
    #return a(c)(b)
    return compose(compose(a, c), b)


def dove(a: Callable, b: Callable, c: Callable, d: Callable) -> Callable:
    #return a(b)(c(d))
    return compose(compose(a, b), c, d)

def eagle(a: Callable, b: Callable, c: Callable, d: Callable, e: Callable) -> Callable:
    #return a(b)(c(d)(e))
    return compose(compose(a, b), compose(c, d), e)

def finch(a: Callable, b: Callable, c: Callable) -> Callable:
    #return c(b)(a)
    return compose(compose(c, b), a)


def goldfinch(a: Callable, b: Callable, c: Callable, d: Callable) -> Callable:
    #return a(d)(b(c))
    return compose(compose(a, d), b, c)

def hummingbird(a: Callable, b: Callable, c: Callable) -> Callable:
    #return a(b)(c)(b)
    return compose(compose(compose(a, b), c), b)

def idiot(a: Callable) -> Callable:
    return a

def jay(a: Callable, b: Callable, c: Callable, d: Callable) -> Callable:
    #return a(b)(a(d)(c))
    return compose(compose(a, b), compose(a, d), c)

def kestrel(a: Callable, b: Callable) -> Callable:
    return a

def kite(a: Callable, b: Callable) -> Callable:
    return b

def lark(a: Callable, b: Callable) -> Callable:
    #return a(b(b))
    return compose(a, b, b)

def mockingbird(a: Callable) -> Callable:
    return compose(a, a)

def owl(a: Callable, b: Callable) -> Callable:
    #return b(a(b))
    return compose(b, a, b)

def omega(a: Callable) -> Callable:
    #return (a(a))(a(a))
    return compose(compose(a, a), compose(a, a))

def phoenix(a: Callable, b: Callable, c: Callable, d: Callable) -> Callable:
    #return a(b(d))(c(d))
    return compose(compose(a, b, d), c, d)

def psi(a: Callable, b: Callable, c: Callable, d: Callable) -> Callable:
    #return a(b(c))(b(d))
    return compose(compose(a, b, c), b, d)

def queer(a: Callable, b: Callable, c: Callable) -> Callable:
    #return b(a(c))
    return compose(b, a, c)

def robin(a: Callable, b: Callable, c: Callable) -> Callable:
    #return b(c)(a)
    return compose(compose(b, c), a)

def starling(a: Callable, b: Callable, c: Callable) -> Callable:
    #return a(c)(b(c))
    return compose(compose(a, c), b, c)

def thrush(a: Callable, b: Callable) -> Callable:
    #return b(a)
    return compose(b, a)

def turing(a: Callable, b: Callable) -> Callable:
    #return b(a(a)(b))
    return compose(b, compose(compose(a, a), b))

def vireo(a: Callable, b: Callable, c: Callable) -> Callable:
    #return c(a)(b)
    return compose(compose(c, a), b)


def warbler(a: Callable, b: Callable) -> Callable:
    #return a(b)(b)
    return compose(compose(a, b), b)


def y_fixed_point(f: Callable) -> Callable:
    return (lambda x: f(lambda y: x(x)(y)))(lambda x: f(lambda y: x(x)(y)))


# https://lptk.github.io/programming/2019/10/15/simple-essence-y-combinator.html
# Z
def z_fixed_point(g: Callable) -> Callable:
    """
    example:
    ```
    fact = z_fixed_point(lambda rec: lambda x: 1 if x == 0 else rec(x - 1) * x)
    ```
    """
    return (lambda rec: g(lambda y: rec(rec)(y)))(lambda rec: g(lambda y: rec(rec)(y)))
