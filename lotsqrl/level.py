from lotsqrl import tiles


class Level(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.actors = []
        self.actors_by_team = {}
        self.tiles = [[tiles.CaveFloor for _ in range(width)] for _ in range(height)]
        self.spawns = []
        for i in range(width):
            self.tiles[0][i] = tiles.CaveWall
            self.tiles[height - 1][i] = tiles.CaveWall

        for i in range(height):
            self.tiles[i][0] = tiles.CaveWall
            self.tiles[i][width - 1] = tiles.CaveWall

        self.path_grid = None

    def add_actor(self, actor):
        self.actors.append(actor)
        actor.level = self
        team = actor.team
        if team is not None:
            team_actors = self.actors_by_team.setdefault(team, [])
            team_actors.append(actor)

    def remove_actor(self, actor):
        if actor.level is None and actor not in self.actors:
            return

        self.actors.remove(actor)
        actor.level = None
        team = actor.team
        if team is not None:
            team_actors = self.actors_by_team[team]
            team_actors.remove(actor)

    def get_tile(self, x, y):
        try:
            return self.tiles[y][x]
        except IndexError:
            return None

    def get_actors_by_pos(self, x, y, team=None):
        if team is not None:
            return [
                actor for actor in self.actors_by_team.get(team, [])
                if actor.x == x and actor.y == y
            ]
        return [actor for actor in self.actors if actor.x == x and actor.y == y]

    def get_actors_by_team(self, team):
        return self.actors_by_team.get(team, None)

    def remove_tile(self, x, y):
        self.tiles[y][x] = tiles.CaveFloor
        self.path_grid[y][x] = 1
