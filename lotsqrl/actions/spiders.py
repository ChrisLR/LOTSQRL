from lotsqrl.actions.base import MeleeAttack, TouchAction
from lotsqrl.teams import Team, ActorTypes


class Bite(MeleeAttack):
    base_damage = (1, 4)
    name = "bite"

    def on_hit(self, actor, target):
        game = actor.game
        if actor.is_player:
            game.add_message("You bite %s!" % target.name)
        else:
            game.add_message(actor.name + " bites %s!" % target.name)
        super().on_hit(actor, target)


class BurrowEgg(TouchAction):
    name = "burrow_egg"

    def can_execute(self, actor, target):
        base_result = super().can_execute(actor, target)
        if not base_result:
            return base_result

        if target.actor_type != ActorTypes.Cocoon or target.burrowed:
            return False

        return True

    def execute(self, actor, target):
        actor.game.add_message("%s burrows into %s!" % (self.name, target.name))
        target.burrowed = True
        actor.level.remove_actor(actor)

        return True
