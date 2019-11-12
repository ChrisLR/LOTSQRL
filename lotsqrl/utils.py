from bearlibterminal import terminal
from lotsqrl import tiles
import math


def get_closest_actor(origin, actors):
    return min(actors, key=lambda actor: get_distance(origin, actor))


def get_actor_delta(actor, target):
    return target.x - actor.x, target.y - actor.y


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
    level = actor.level
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

        if level.get_tile(line_x, line_y) != tiles.CaveFloor:
            return False

    return True


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
