from sumps.ecs.entity import Component, EntityManager, Struct


class Velocity(Struct):
    x: float = 0.0
    y: float = 0.0


class Position(Struct):
    x: int = 0
    y: int = 0


def qualified_name(c: type[Component]) -> str:
    return c.__name__


def test_entity_manager():
    em = EntityManager()
    e1 = em.create_entity(Position(x=5, y=5), Velocity(x=0.9, y=1.2))
    e2 = em.create_entity(Position(x=25, y=25), Velocity(x=1.9, y=2.2))

    assert em.entity_exists(e1)
    assert em.entity_exists(e2)

    p1 = em.component_for_entity(e1, Position)
    assert p1 == Position(x=5, y=5)
    assert em.component_for_entity(e2, Velocity) == Velocity(x=1.9, y=2.2)

    results = em.get_components(Position, Velocity)
    assert results
    assert (e1, (Position(x=5, y=5), Velocity(x=0.9, y=1.2))) in results

    e = em.get_entity(e1)
    assert e.position == Position(x=5, y=5)

    e = em.get_entity(e2)
    assert e.velocity == Velocity(x=1.9, y=2.2)
