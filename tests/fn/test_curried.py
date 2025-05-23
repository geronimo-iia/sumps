from sumps.func.curried import curried


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
