from lotsqrl import bumpers, components, controllers
from lotsqrl.gameobjects import GameObject, Corpse
from lotsqrl.messages import MessageScope


class Actor(GameObject):
    actor_type = None
    base_actions = tuple()
    default_controller = controllers.AIController
    evolution_worth = 1

    def __init__(self, game, hp, name="", x=0, y=0, team=None,
                 ascii_char="", ascii_color="white", tile_char="", display_priority=9):
        super().__init__(game, name, x, y, team, ascii_char, ascii_color, tile_char, display_priority)
        self.actions = components.Action(self, self.base_actions)
        self.cooldowns = components.Cooldowns(self)
        self.dead = False
        self.health = components.Health(self, hp)
        self.stunned = 0
        self.target = None
        self.path_find = None
        self.path_find_runs = None
        self.controller = self.default_controller(self)
        self.evolution = None
        self.corpse = None
        self.effects = components.Effects(self)
        self.armor = components.Armor(self)
        self.bumper = bumpers.Null(self)

    def act(self):
        controller = self.controller
        can_act = controller.can_act()
        if can_act:
            return controller.act()
        return can_act

    def on_death(self, leave_corpse=True):
        if self.dead:
            return

        self.blocking = False
        self.dead = True
        self.game.messaging.add_scoped_message(
            message_actor="You are dead!",
            message_others=f"{self.name} is dead!",
            scope=MessageScope.TargetsPlayer,
            actor=self
        )
        self.effects.on_death()
        self.game.level.remove_actor(self)
        if leave_corpse:
            self.corpse = Corpse(self.game, self.name, self.x, self.y, evolution_worth=self.evolution_worth)
            self.game.level.add_actor(self.corpse)

    def update(self):
        super().update()
        self.cooldowns.update()
        self.effects.update()
