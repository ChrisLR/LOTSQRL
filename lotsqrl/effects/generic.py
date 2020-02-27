from lotsqrl.effects.base import Effect


class Poison(Effect):
    name = "poison"

    def __init__(self, host, lifetime, damage_per_turn, poisoner=None):
        super().__init__(host, lifetime)
        self.damage_per_turn = damage_per_turn
        self.poisoner = poisoner

    def update(self):
        super().update()
        if self.host.health.hp >= 0:
            self.host.health.damage(self.damage_per_turn)
            if self.host.health.hp <= 0:
                self.lifetime = 0
                host = self.host
                host.game.messaging.add_scoped_message(
                    message_actor=f"{host.name} died from your poison!",
                    message_target=f"You died from poisoning!",
                    message_others=f"{host.name} has died from poisoning!",
                    target=host, actor=self.poisoner,
                )
                if self.poisoner and self.poisoner.score:
                    self.poisoner.score.kills += 1

    def on_start(self):
        host = self.host
        host.game.messaging.add_scoped_message(
            message_actor=f"You have been poisoned!",
            actor=host
        )

    def on_finish(self):
        host = self.host
        host.game.messaging.add_scoped_message(
            message_actor=f"You are no longer poisoned",
            actor=host
        )

    def on_cancel(self):
        self.on_finish()
