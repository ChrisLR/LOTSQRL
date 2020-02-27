from lotsqrl.armors.base import Armor
from lotsqrl.effects import Poison


class ThickChitin(Armor):
    def reduce(self, damage):
        return int(damage / 2)


class SpikedChitin(ThickChitin):
    def on_damaged(self, damage, attacker):
        if attacker.health.hp > 0:
            attacker.health.damage(2)
            if attacker.health.hp <= 0:
                self.host.game.messaging.add_scoped_message(
                    message_actor=f"{attacker.name} impales itself on your spikes!",
                    message_target=f"You impale yourself on {self.host.name}'s spikes!",
                    message_others=f"{attacker.name} impales itself on {self.host.name}'s spikes!",
                    actor=self.host, target=attacker
                )


class PoisonousHairs(SpikedChitin):
    def on_damaged(self, damage, attacker):
        super().on_damaged(damage, attacker)
        if attacker.health.hp > 0:
            if not attacker.effects.get_by_name("poison"):
                attacker.effects.set(Poison(attacker, -1, 2, self.host))
