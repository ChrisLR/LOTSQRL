from lotsqrl.actions.base import MeleeAttack


class Stab(MeleeAttack):
    base_damage = (1, 4)
    name = "stab"

    def on_hit(self, actor, target):
        game = actor.game
        game.add_message(self.name + " stabs %s!" % target.name)
        super().on_hit(actor, target)
