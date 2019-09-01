from bearlibterminal import terminal


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
    return abs(target.x - actor.x) + abs(target.y - actor.y)


def get_directional_pos():
    handled = None
    while not handled:
        press = terminal.read()
        direction_offset = direction_offsets.get(press)
        if direction_offset is not None:
            return direction_offset

        if press == terminal.TK_ESCAPE:
            return


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
