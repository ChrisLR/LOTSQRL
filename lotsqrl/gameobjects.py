from lotsqrl.teams import ActorTypes, Team
from lotsqrl import components


class GameObject(object):
    def __init__(self, game, name="", x=0, y=0, team=None,
                 ascii_char="", ascii_color="white", tile_char="", display_priority=10):
        self.game = game
        self.name = name
        self.x = x
        self.y = y
        self.level = None
        self.blocking = True
        self.team = team
        self.is_player = False
        self.display_priority = 10
        self.score = None
        self.display = components.Display(self, ascii_char, ascii_color, tile_char, display_priority)

    def update(self):
        pass


class Corpse(GameObject):
    actor_type = ActorTypes.Corpse

    def __init__(self, game, name, x=0, y=0, evolution_worth=1):
        super().__init__(game, "the corpse of %s" % name, x, y, "%")
        self.blocking = False
        self.team = Team.Corpse
        self.dead = True
        self.evolution_worth = evolution_worth
        self.evolution = None

    def act(self):
        pass


class GridTarget(object):
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y


class TargetLine(object):
    def __init__(self, actor, target, coordinates):
        self.actor = actor
        self.target = target
        self.coordinates = coordinates
        self.level = actor.level

    def __iter__(self):
        yield from self.coordinates
