import random

from lotsqrl.level import Level
from lotsqrl import tiles as tile_types


def count_alive_neighbours(tiles, x, y):
    count = 0
    for i in range(-1, 2):
        for j in range(-1, 2):
            neighbour_x = x + i
            neighbour_y = y + j
            if i == 0 and j == 0:
                pass
            elif neighbour_x < 0 or neighbour_y < 0 or neighbour_x >= len(tiles) or neighbour_y >= len(tiles[0]):
                count = count + 1
            elif tiles[neighbour_x][neighbour_y] == tile_types.CaveWall:
                count = count + 1

    return count


def do_simulation_step(old_tiles, width, height, birth_limit, death_limit):
    new_tiles = [[tile_types.CaveFloor for _ in range(width)] for _ in range(height)]
    for x in range(len(old_tiles)):
        for y in range(len(old_tiles[x])):
            nbs = count_alive_neighbours(old_tiles, x, y)
            if old_tiles[x][y] == tile_types.CaveWall:
                if nbs < death_limit:
                    new_tiles[x][y] = tile_types.CaveFloor
                else:
                    new_tiles[x][y] = tile_types.CaveWall
            else:
                if nbs > birth_limit:
                    new_tiles[x][y] = tile_types.CaveWall
                else:
                    new_tiles[x][y] = tile_types.CaveFloor

    return new_tiles


def generate_map(width, height, number_of_steps):
    tries = 10
    new_level = Level(width, height)
    while tries:
        try:
            map_cells = generate_tiles(width, height, number_of_steps)
            spawns = seek_spawn_points(map_cells)

            if len(spawns) >= 6:
                new_level.tiles = map_cells
                new_level.spawns = spawns
                new_level.path_grid = [[0 if c == tile_types.CaveWall else 1 for c in row] for row in map_cells]
                return new_level

        except ValueError:
            pass
        tries -= 1

    raise ValueError("Map could not generate with enough spawn points")


def random_alive(chance):
    if random.randint(0, 100) <= chance:
        return tile_types.CaveWall
    return tile_types.CaveFloor


def generate_tiles(width, height, number_of_steps):
    tiles = [[random_alive(30) for _ in range(width)] for _ in range(height)]
    for _ in range(number_of_steps):
        tiles = do_simulation_step(tiles, width, height, 4, 3)

    return tiles


def seek_spawn_points(tiles):
    possible_coordinates = []
    top_row = tiles[0]
    for x, tile in enumerate(top_row):
        if tile == tile_types.CaveFloor:
            possible_coordinates.append((x, 0))

    bottom_row = tiles[-1]
    for x, tile in enumerate(bottom_row):
        if tile == tile_types.CaveFloor:
            possible_coordinates.append((x, len(bottom_row) - 1))

    for y, row in enumerate(tiles):
        left_tile = row[0]
        if left_tile == tile_types.CaveFloor:
            possible_coordinates.append((0, y))

        right_tile = row[-1]
        if right_tile == tile_types.CaveFloor:
            possible_coordinates.append((len(row) - 1, y))

    return possible_coordinates
