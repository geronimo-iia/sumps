"""Combinators."""


def apply(a, b):
    # (S(K))(S(K))
    return a(b)


def bluebird(a, b, c):
    # S(KS)K
    return a(b(c))


def blackbird(a, b, c, d):
    # (S(K(S(KS)K)))(S(KS)K)
    return a(b(c)(d))


def cardinal(a, b, c):
    # ((S((S(K(S(KS)K)))S))(KK))
    return a(c)(b)


def dove(a, b, c, d):
    # (S(K(S(KS)K)))
    return a(b)(c(d))


def eagle(a, b, c, d, e):
    ##(S(K((S(K(S(KS)K)))((S(KS))K))))
    return a(b)(c(d)(e))


def finch(a, b, c):
    # ((S(K((S((SK)K))(K((S(K(S((SK)K))))K)))))((S(K((S(K(S(KS)K)))((S(KS))K))))((S(K(S((SK)K))))K)))
    return c(b)(a)


def goldfinch(a, b, c, d):
    # ((S(K(S(KS)K)))((S((S(K(S(KS)K)))S))(KK)))
    return a(d)(b(c))


def hummingbird(a, b, c):
    # ((S(K((S(K(S((S(K((S((SK)K))((SK)K))))((S(K(S(KS)K)))((S(K(S((SK)K))))K))))))K)))(S(K((S((S(K(S(KS)K)))S))(KK)))))
    return a(b)(c)(b)


def idiot(a):
    # SKK
    return a


def jay(a, b, c, d):
    # ((S(K(S(K((S((S(K(S(KS)K)))S))(KK))))))((S((S(K((S((SK)K))((SK)K))))((S(K(S(
    # KS)K)))((S(K(S((SK)K))))K))))(K((S(K((S
    # ((S(K(S(KS)K)))S))(KK))))(S(K((S(K(S(KS)K)))((S(KS))K))))))))
    return a(b)(a(d)(c))


def kestrel(a, b):
    # K
    return a


def kite(a, b):
    # (K((SK)K))
    return b


def lark(a, b):
    # ((S((S(KS))K))(K((S((SK)K))((SK)K))))
    return a(b(b))


def mockingbird(a):
    # ((S((SK)K))((SK)K))
    return a(a)


def owl(a, b):
    # (S((SK)K))
    return b(a(b))


def omega(a):
    # (((S((SK)K))((SK)K))((S((SK)K))((SK)K)))
    return (a(a))(a(a))


def phoenix(a, b, c, d):
    return a(b(d))(c(d))


def psi(a, b, c, d):
    return a(b(c))(b(d))


def queer(a, b, c):
    # ((S(K(S((S(KS))K))))K)
    return b(a(c))


def robin(a, b, c):
    # ((S(K(S(KS)K)))((S(K(S((SK)K))))K))
    return b(c)(a)


def starling(a, b, c):
    # S
    return a(c)(b(c))


def thrush(a, b):
    # ((S(K(S((SK)K))))K)
    return b(a)


def turing(a, b):
    # ((S(K(S((SK)K))))((S((SK)K))((SK)K)))
    return b(a(a)(b))


def vireo(a, b, c):
    # ((S(K((S((S(K(S(KS)K)))S))(KK))))((S(K(S((SK)K))))K))
    return c(a)(b)


def warbler(a, b):
    # ((S(K(S((S(K((S((SK)K))((SK)K))))((S(K(S(KS)K)))((S(K(S((SK)K))))K))))))K)
    return a(b)(b)


def y_fixed_point(f):
    return (lambda x: f(lambda y: x(x)(y)))(lambda x: f(lambda y: x(x)(y)))


# https://lptk.github.io/programming/2019/10/15/simple-essence-y-combinator.html
# Z
def z_fixed_point(g):
    """
    example:
    ```
    fact = z_fixed_point(lambda rec: lambda x: 1 if x == 0 else rec(x - 1) * x)
    ```
    """
    return (lambda rec: g(lambda y: rec(rec)(y)))(lambda rec: g(lambda y: rec(rec)(y)))
