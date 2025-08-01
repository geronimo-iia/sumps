from sumps.func.curried import curried

# 24, 29, 34, 39, 44, 51, 58, 65, 72, 75, 97-113


@curried
def dummy_0():
    return 0


@curried
def dummy_1(a):
    return 1 + a


@curried
def dummy_2(a, b):
    return 1 + a + b


@curried
def dummy_3(a, b, c):
    return 1 + a + b + c


@curried
def dummy_5(a, b, c, d, e):
    return 1 + a + b + c + d + e


@curried
def dummy_6(a, b, c, d, e, f):
    return 1 + a + b + c + d + e + f


@curried
def dummy_7(a, b, c, d, e, f, g):
    return 1 + a + b + c + d + e + f + g


@curried
def add_1(a, b, c, d):
    return a + b + c + d


def test_curried_simple():
    assert add_1(1, 1, 1, 1) == 4
    assert add_1(1, 1, 1)(1) == 4
    assert add_1(1, 1)(1, 1) == 4
    assert add_1(1, 1)(1)(1) == 4
    assert add_1(1)(1)(1, 1) == 4

    plusone = add_1(1)
    assert plusone(3, 1, 1) == 6
    assert plusone(3, 1, 2) == 7

    plustwo = plusone(1)

    assert plustwo(3, 1) == 6
    assert plustwo(2, 8) == 12
