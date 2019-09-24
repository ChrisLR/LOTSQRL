from lotsqrl.actions.base import MeleeAttack


class Stab(MeleeAttack):
    base_damage = (1, 4)

    def on_hit(self, target):
        self.game.add_message(self.name + " stabs %s!" % target.name)
        super().on_hit(target)
