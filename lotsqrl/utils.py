import contextlib

from bearlibterminal import terminal

from lotsqrl import tiles
from lotsqrl.gameobjects import TargetLine
from lotsqrl.teams import Team


def get_closest_actor(origin, actors):
    return min(actors, key=lambda actor: get_distance(origin, actor))


def get_actor_delta(actor, target):
    return target.x - actor.x, target.y - actor.y


def get_directional_delta(actor, target):
    x, y = get_actor_delta(actor, target)
    return sign(x), sign(y)


def sign(number):
    if number > 0:
        return 1
    elif number == 0:
        return 0
    elif number < 0:
        return -1


def get_distance(actor, target):
    dx = abs(target.x - actor.x)
    dy = abs(target.y - actor.y)

    return dx if dx > dy else dy


def get_directional_pos():
    handled = None
    while not handled:
        press = terminal.read()
        direction_offset = direction_offsets.get(press)
        if direction_offset is not None:
            return direction_offset

        if press == terminal.TK_ESCAPE:
            return


def has_clear_line_of_sight(actor, target):
    target_line = get_target_line(actor, target)
    if get_obstacles_in_target_line(target_line, include_actors=False):
        return False
    return True


def is_in_direct_line(actor, target):
    dx, dy = get_actor_delta(actor, target)
    if abs(dx) == abs(dy):
        # Diagonals
        return True
    elif dx == 0 or dy == 0:
        return True
    return False


def is_allied(actor, target):
    # Just a basic way, should end up using a component
    if actor.team == target.team:
        return True
    return False


def is_enemy(actor, target):
    # Just a basic way, should end up using a component
    if actor.team is Team.SpiderQueen and target.team is Team.Goblin:
        return True
    elif actor.team is Team.Goblin and target.team is Team.SpiderQueen:
        return True
    return False


def get_closest_floor_in_line(target_line):
    level = target_line.level
    for coord in target_line:
        if level.get_tile(*coord) == tiles.CaveFloor:
            return coord


def get_obstacles_in_target_line(target_line, include_walls=True, include_actors=True):
    actor = target_line.actor
    level = target_line.level
    target = target_line.target
    obstacles = []
    for coord in target_line:
        x, y = coord
        if include_walls:
            tile = level.get_tile(x, y)
            if tile != tiles.CaveFloor:
                obstacles.append(tile)

        if include_actors:
            actors = [a for a in level.get_actors_by_pos(x, y)
                      if a is not actor and a is not target and a.blocking]
            obstacles.extend(actors)

    return obstacles


def get_target_line(actor, target):
    coords = []
    line_x, line_y = actor.x, actor.y
    delta_x, delta_y = get_actor_delta(actor, target)
    sign_x, sign_y = sign(delta_x), sign(delta_y)

    reached_x = False
    reached_y = False
    while not (reached_x and reached_y):
        if line_x == target.x:
            reached_x = True
        else:
            line_x += sign_x

        if line_y == target.y:
            reached_y = True
        else:
            line_y += sign_y

        if not (reached_x and reached_y):
            coords.append((line_x, line_y))

    return TargetLine(actor, target, coords)


@contextlib.contextmanager
def silence(game):
    game.messaging.silent = True
    yield
    game.messaging.silent = False


direction_offsets = {
    terminal.TK_KP_8: (0, -1),
    terminal.TK_KP_9: (1, -1),
    terminal.TK_KP_6: (1, 0),
    terminal.TK_KP_3: (1, 1),
    terminal.TK_KP_2: (0, 1),
    terminal.TK_KP_1: (-1, 1),
    terminal.TK_KP_4: (-1, 0),
    terminal.TK_KP_7: (-1, -1)
}

direction_offsets_char = {
    (0, -1): "|",
    (1, -1): "/",
    (1, 0): "-",
    (1, 1): "\\",
    (0, 1): "|",
    (-1, 1): "/",
    (-1, 0): "-",
    (-1, -1): "\\"
}
