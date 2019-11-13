from lotsqrl.teams import ActorTypes, Team


class GameObject(object):
    ascii_color = "white"

    def __init__(self, game, display_char="", name="", x=0, y=0, team=None):
        self.game = game
        self.display_char = display_char
        self.name = name
        self.x = x
        self.y = y
        self.level = None
        self.blocking = True
        self.team = team
        self.is_player = False
        self.display_priority = 10
        self.score = None

    def ascii_str(self):
        return "[color=%s]%s[/color]" % (self.ascii_color, self.display_char)

    def update(self):
        pass


class Corpse(GameObject):
    actor_type = ActorTypes.Corpse

    def __init__(self, game, name, x=0, y=0):
        super().__init__(game, "%", "the corpse of %s" % name, x, y)
        self.blocking = False
        self.team = Team.Corpse
        self.dead = True

    def act(self):
        pass


class GridTarget(object):
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
