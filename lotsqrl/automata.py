def count_alive_neighbours(map, x, y):
    count = 0
    for i in range(-1, 2):
        for j in range(-1, 2):
            neighbour_x = x + i
            neighbour_y = y + j
            if i == 0 and j == 0:
                pass
            elif neighbour_x < 0 or neighbour_y < 0 or neighbour_x >= len(map) or neighbour_y >= len(map[0]):
                count = count + 1
            elif map[neighbour_x][neighbour_y] == "#":
                count = count + 1

    return count


def do_simulation_step(old_map, width, height, birth_limit, death_limit):
    new_map = [["." for _ in range(width)] for _ in range(height)]
    for x in range(len(old_map)):
        for y in range(len(old_map[x])):
            nbs = count_alive_neighbours(old_map, x, y)
            if old_map[x][y] == "#":
                if nbs < death_limit:
                    new_map[x][y] = "."
                else:
                    new_map[x][y] = "#"
            else:
                if nbs > birth_limit:
                    new_map[x][y] = "#"
                else:
                    new_map[x][y] = "."

    return new_map


def rando_alive(chance):
    if random.randint(0, 100) <= chance:
        return "#"
    return "."


def generate_map(width, height, number_of_steps):
    tries = 10
    new_level = Level(width, height)
    while tries:
        map_cells = generate_map_cells(width, height, number_of_steps)
        spawns = seek_spawn_points(map_cells)
        if len(spawns) >= 6:
            new_level.tiles = map_cells
            new_level.spawns = spawns
            return new_level
        tries -= 1

    raise ValueError("Map could not generate with enough spawn points QQ")


def generate_map_cells(width, height, number_of_steps):
    map_cells = [[rando_alive(30) for _ in range(width)] for _ in range(height)]
    for _ in range(number_of_steps):
        map_cells = do_simulation_step(map_cells, width, height, 4, 3)

    return map_cells