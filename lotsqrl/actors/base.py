from lotsqrl.teams import Team, ActorTypes
from lotsqrl import components


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


class Actor(GameObject):
    actor_type = None
    base_actions = tuple()

    def __init__(self, game, hp, display_char="", name="", x=0, y=0, team=None):
        super().__init__(game, display_char, name, x, y, team=team)
        self.actions = components.Action(self, self.base_actions)
        self.cooldowns = components.Cooldowns(self)
        self.hp = hp
        self.max_hp = hp
        self.dead = False
        self.display_priority = 9
        self.stunned = 0
        self.target = None
        self.path_find = None
        self.path_find_runs = None

    def act(self):
        pass

    def bump(self, target):
        pass

    def on_death(self):
        self.blocking = False
        self.dead = True
        self.display_char = "%"
        self.display_priority = 10
        self.game.add_message(self.name + " is dead!")
        corpse = Corpse(self.game, self.name, self.x, self.y)
        self.game.level.remove_actor(self)
        self.game.level.add_actor(corpse)

    def update(self):
        super().update()
        self.cooldowns.update()


class Corpse(GameObject):
    actor_type = ActorTypes.Corpse

    def __init__(self, game, name, x=0, y=0):
        super().__init__(game, "%", "the corpse of %s" % name, x, y)
        self.blocking = False
        self.team = Team.Corpse
        self.dead = True

    def act(self):
        pass
