from lotsqrl.effects.base import Effect


class Digesting(Effect):
    name = "Digesting"

    def __init__(self, host, lifetime, target, regen_per_turn, damage_per_turn):
        super().__init__(host, lifetime)
        self.regen_per_turn = regen_per_turn
        self.target = target
        self.damage_per_turn = damage_per_turn

    def update(self):
        super().update()
        self.host.hp += self.regen_per_turn
        self.target.hp -= self.damage_per_turn
        if self.target.hp <= 0:
            self.lifetime = 0

    def on_start(self):
        host = self.host
        host.game.messaging.add_scoped_message(
            message_actor=f"You start digesting {self.target.name}!",
            message_target=f"You are being digested!!",
            actor=host, target=self.target
        )

    def on_finish(self):
        host = self.host
        host.game.messaging.add_scoped_message(
            message_actor=f"You finish digesting {self.target.name}!",
            message_target=f"You have been dissolved!!",
            actor=host, target=self.target
        )
        self.target.on_death(leave_corpse=False)

    def on_cancel(self):
        self.on_death()

    def on_death(self):
        host = self.host
        host.game.messaging.add_scoped_message(
            message_actor=f"{self.target} escapes from you!",
            message_target=f"You escaped from {self.host}!",
            message_others=f"{self.target} escapes from {self.host}",
            actor=host, target=self.target
        )
        self.target.x = host.x
        self.target.y = host.y
        self.host.game.level.add_actor(self.target)
