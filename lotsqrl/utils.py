def get_closest_actor(origin, actors):
    return min(actors, key=lambda actor: get_distance(origin, actor))


def step_to_target(actor, target):
    target_dx, target_dy = get_actor_delta(actor, target)
    sx = sign(target_dx)
    sy = sign(target_dy)
    tx = actor.x + sx
    ty = actor.y + sy

    result = move_to(actor, tx, ty)
    if result:
        return result

    fx, fy = avoid_obstacle(actor, target, sx, sy)

    return move_to(actor, actor.x + fx, actor.y + fy)


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


def avoid_obstacle(actor, target, offset_x, offset_y):
    if abs(target.x - actor.x) > abs(target.y - actor.y):
        if offset_y == 0:
            return offset_x, random.choice([-1, 1])
        else:
            return offset_x, offset_y * -1
    if offset_x == 0:
        return random.choice([-1, 1]), offset_y
    return offset_x * -1, offset_y


def seek_spawn_points(map_cells):
    possible_coordinates = []
    top_row = map_cells[0]
    for x, tile in enumerate(top_row):
        if tile == ".":
            possible_coordinates.append((x, 0))

    bottom_row = map_cells[-1]
    for x, tile in enumerate(bottom_row):
        if tile == ".":
            possible_coordinates.append((x, len(bottom_row) - 1))

    for y, row in enumerate(map_cells):
        left_tile = row[0]
        if left_tile == ".":
            possible_coordinates.append((0, y))

        right_tile = row[-1]
        if right_tile == ".":
            possible_coordinates.append((len(row) - 1, y))

    return possible_coordinates



def select_player_spawn(level):
    middle_x, middle_y = int(level.width / 2), int(level.height / 2)
    if level.get_tile(middle_x, middle_y) == ".":
        return middle_x, middle_y
    tries = 20
    while tries:
        middle_x += random.randint(-10, 10)
        middle_y += random.randint(-10, 10)
        if level.get_tile(middle_x, middle_y) == ".":
            return middle_x, middle_y
        tries -= 1

    raise ValueError("Could not find player spawn QQ")