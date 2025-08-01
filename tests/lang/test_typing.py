import pytest
from msgspec import Struct

from sumps.lang.typing import Intersection


class A:
    def i_can_fly(self):
        return True


class B:
    def i_beleive(self):
        return True


class Velocity(Struct):
    x: float = 0.0
    y: float = 0.0


class Position(Struct):
    x: int = 0
    y: int = 0


class TestIntersection:
    def test_basic_intersection(self):
        ab_cls = Intersection([A, B])
        ab = ab_cls()

        assert ab.i_can_fly
        assert ab.i_beleive
        assert ab.i_beleive()
        assert ab.i_can_fly()

    def test_intersection_overlap(self):
        with pytest.raises(TypeError):  # TypeError: multiple bases have instance lay-out conflict
            Intersection([Velocity, Position])

    def test_intersection_none_type(self):
        with pytest.raises(TypeError):
            Intersection([Velocity, type(None)])

    def test_intersection_builtins_type(self):
        with pytest.raises(TypeError):
            Intersection([Velocity, str])

    def test_intersection_single_type(self):
        assert Intersection([Velocity]) == Velocity

    def test_intersection_deduplicate(self):
        abb_cls = Intersection([A, B, B])
        abb = abb_cls()

        assert abb.i_can_fly
        assert abb.i_beleive
        assert abb.i_beleive()
        assert abb.i_can_fly()
