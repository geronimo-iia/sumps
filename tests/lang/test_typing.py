import pytest
from msgspec import Struct
from msgspec.structs import asdict

from sumps.lang.typing import Archetype, Intersection


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


def test_intesection():
    ab_cls = Intersection([A, B])

    ab = ab_cls()

    assert ab.i_can_fly
    assert ab.i_beleive

    assert ab.i_beleive()
    assert ab.i_can_fly()


def test_intesection_overlab():
    with pytest.raises(TypeError):  # TypeError: multiple bases have instance lay-out conflict
        Intersection([Velocity, Position])


def test_archetype():
    sprite = Archetype(name="sprite", attributs=[Position, Velocity])
    assert sprite
    item = sprite(position=Position(x=0, y=1), velocity=Velocity(x=0, y=1))

    assert item
    assert asdict(item) == {"position": Position(x=0, y=1), "velocity": Velocity(x=0, y=1)}
