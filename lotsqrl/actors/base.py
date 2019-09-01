class GameObject(object):
    def __init__(self, display_char="", name="", x=0, y=0, team=None):
        self.display_char = display_char
        self.name = name
        self.x = x
        self.y = y
        self.level = None
        self.blocking = True
        self.team = team
        self.is_player = False
        self.display_priority = 10


class Actor(GameObject):
    def __init__(self, hp, display_char="", name="", x=0, y=0, team=None):
        super().__init__(display_char, name, x, y, team=team)
        self.hp = hp
        self.max_hp = hp
        self.dead = False
        self.display_priority = 9
        self.stunned = 0

    def act(self):
        pass

    def bump(self, target):
        pass

    def on_death(self):
        self.blocking = False
        self.dead = True
        self.display_char = "%"
        self.display_priority = 10
        messages.append(self.name + " is dead!")
