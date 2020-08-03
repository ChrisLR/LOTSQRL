import random

from bearlibterminal import terminal
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

from lotsqrl import tiles, utils
from lotsqrl.messages import MessageScope


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


def wait(actor):
    return True


def move_to(actor, x, y, bump=True):
    level = actor.level
    if not level:
        return

    if level.get_tile(x, y) == tiles.CaveFloor:
        collides = actor.level.get_actors_by_pos(x, y)
        collision = next((collide for collide in collides if collide is not actor and collide.blocking), None)
        if collision is not None and bump is True:
            return actor.bumper.bump(collision)
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
    terminal.TK_KP_7: move_northwest,
    terminal.TK_KP_5: wait
}


def step_to_target(actor, target):
    if actor.path_find_runs:
        actor.path_find_runs -= 1
        if actor.path_find_runs <= 0:
            actor.path_find = None

    if actor.path_find:
        next_x, next_y = actor.path_find.pop(0)
        success = move_to(actor, next_x, next_y)
        if not success:
            actor.path_find = None
            actor.path_find_runs = None
        else:
            return success

    target_dx, target_dy = utils.get_actor_delta(actor, target)
    sx = utils.sign(target_dx)
    sy = utils.sign(target_dy)
    tx = actor.x + sx
    ty = actor.y + sy

    result = move_to(actor, tx, ty)
    if result:
        return result

    path, runs = path_find(actor, target)
    if path:
        actor.path_find = path
        actor.path_find_runs = 5 if runs > 5 else runs
        next_x, next_y = path.pop(0)
        success = move_to(actor, next_x, next_y)
        if not success:
            actor.path_find = None
            actor.path_find_runs = None
            target_dx, target_dy = utils.get_actor_delta(actor, target)
            sx = utils.sign(target_dx)
            sy = utils.sign(target_dy)
            ax, ay = avoid_obstacle(actor, target, sx, sy)
            return move_to(actor, actor.x + ax, actor.y + ay)
        return success
    else:
        actor.level.remove_tile(tx, ty)
        actor.game.messaging.add_scoped_message(
            message_others=actor.name + " digs through rock.",
            scope=MessageScope.All,
            actor=actor
        )
        return True


def path_find(actor, target):
    level = actor.level
    if not level:
        return None, 0

    grid = Grid(matrix=level.path_grid)
    start = grid.node(actor.x, actor.y)
    end = grid.node(target.x, target.y)
    finder = AStarFinder(diagonal_movement=DiagonalMovement.always)
    path, runs = finder.find_path(start, end, grid)

    return path[1::], runs
