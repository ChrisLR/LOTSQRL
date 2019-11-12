import pytest

from lotsqrl import actors, tiles, utils
from lotsqrl.level import Level


def test_get_closest_actor_returns_closest_actor():
    actor = actors.Egg(None, 0, 0)
    closest = actors.Cocoon(None, 1, 0)
    all_objects = [closest, actors.Goblin(None, 2, 2), actors.Goblin(None, 1, 1)]

    result = utils.get_closest_actor(actor, all_objects)
    assert result is closest


@pytest.mark.parametrize("expected, target_position", [
    (1, (1, 1)), (2, (2, 2)), (3, (2, 3)), (3, (-2, -3))])
def test_get_distance_returns_actual_distance(expected, target_position):
    actor = actors.Egg(None, 0, 0)
    tx, ty = target_position
    target = actors.Goblin(None, tx, ty)
    result = utils.get_distance(actor, target)

    assert result == expected


@pytest.mark.parametrize("target_position", [(1, 1), (2, 3), (8, 8)])
def test_clear_line_of_sight_returns_true_when_clear(target_position):
    tx, ty = target_position
    level = Level(10, 10)
    actor = actors.Spider(None, 5, 5)
    actor.level = level
    target = actors.Goblin(None, tx, ty)
    result = utils.has_clear_line_of_sight(actor, target)

    assert result is True


def test_clear_line_of_sight_returns_false_when_obstructed():
    level = Level(10, 10)
    level.tiles[1][2] = tiles.CaveWall
    level.tiles[2][2] = tiles.CaveWall
    level.tiles[3][2] = tiles.CaveWall

    actor = actors.Spider(None, 5, 2)
    actor.level = level
    target = actors.Goblin(None, 1, 2)
    result = utils.has_clear_line_of_sight(actor, target)

    assert result is False
