class Level(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.actors = []
        self.tiles = [["." for _ in range(width)] for _ in range(height)]
        self.spawns = []
        for i in range(width):
            self.tiles[0][i] = "#"
            self.tiles[height - 1][i] = "#"

        for i in range(height):
            self.tiles[i][0] = "#"
            self.tiles[i][width - 1] = "#"

    def add_actor(self, actor):
        self.actors.append(actor)
        actor.level = self

    def remove_actor(self, actor):
        self.actors.remove(actor)
        actor.level = None

    def get_tile(self, x, y):
        try:
            return self.tiles[y][x]
        except IndexError:
            return None

    def get_actors(self, x, y):
        return [actor for actor in self.actors if actor.x == x and actor.y == y]
