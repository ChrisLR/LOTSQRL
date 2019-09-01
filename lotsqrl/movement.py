import random

from bearlibterminal import terminal

from lotsqrl import utils


def avoid_obstacle(actor, target, offset_x, offset_y):
    if abs(target.x - actor.x) > abs(target.y - actor.y):
        if offset_y == 0:
            return offset_x, random.choice([-1, 1])
        else:
            return offset_x, offset_y * -1
    if offset_x == 0:
        return random.choice([-1, 1]), offset_y
    return offset_x * -1, offset_y


def move_north(actor):
    return move_to(actor, actor.x, actor.y - 1)


def move_northeast(actor):
    return move_to(actor, actor.x + 1, actor.y - 1)


def move_east(actor):
    return move_to(actor, actor.x + 1, actor.y)


def move_southeast(actor):
    return move_to(actor, actor.x + 1, actor.y + 1)


def move_south(actor):
    return move_to(actor, actor.x, actor.y + 1)


def move_southwest(actor):
    return move_to(actor, actor.x - 1, actor.y + 1)


def move_west(actor):
    return move_to(actor, actor.x - 1, actor.y)


def move_northwest(actor):
    return move_to(actor, actor.x - 1, actor.y - 1)


def move_to(actor, x, y, bump=True):
    level = actor.level
    if not level:
        return

    if level.get_tile(x, y) == ".":
        collides = actor.level.get_actors(x, y)
        collision = next((collide for collide in collides if collide is not actor and collide.blocking), None)
        if collision is not None and bump is True:
            return actor.bump(collision)
        else:
            actor.x = x
            actor.y = y
            return True
    else:
        return False


move_actions = {
    terminal.TK_KP_8: move_north,
    terminal.TK_KP_9: move_northeast,
    terminal.TK_KP_6: move_east,
    terminal.TK_KP_3: move_southeast,
    terminal.TK_KP_2: move_south,
    terminal.TK_KP_1: move_southwest,
    terminal.TK_KP_4: move_west,
    terminal.TK_KP_7: move_northwest
}


def step_to_target(actor, target):
    target_dx, target_dy = utils.get_actor_delta(actor, target)
    sx = utils.sign(target_dx)
    sy = utils.sign(target_dy)
    tx = actor.x + sx
    ty = actor.y + sy

    result = move_to(actor, tx, ty)
    if result:
        return result

    fx, fy = avoid_obstacle(actor, target, sx, sy)

    return move_to(actor, actor.x + fx, actor.y + fy)
