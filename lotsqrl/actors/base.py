from lotsqrl import components, controllers
from lotsqrl.gameobjects import GameObject, Corpse


class Actor(GameObject):
    actor_type = None
    base_actions = tuple()
    default_controller = controllers.AIController

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
        self.controller = self.default_controller(self)

    def act(self):
        controller = self.controller
        can_act = controller.can_act()
        if can_act:
            return controller.act()
        return can_act

    def bump(self, target):
        pass

    def on_death(self):
        self.blocking = False
        self.dead = True
        self.display_char = "%"
        self.display_priority = 10
        if self.is_player:
            self.game.add_message("You are dead!")
        else:
            self.game.add_message(self.name + " is dead!")
        corpse = Corpse(self.game, self.name, self.x, self.y)
        self.game.level.remove_actor(self)
        self.game.level.add_actor(corpse)

    def update(self):
        super().update()
        self.cooldowns.update()
