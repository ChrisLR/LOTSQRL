from lotsqrl.actions.base import MeleeAttack


class Stab(MeleeAttack):
    base_damage = (1, 4)
    name = "stab"

    def on_hit(self, actor, target):
        game = actor.game
        game.add_message(actor.name + " stabs %s!" % target.name)
        super().on_hit(actor, target)


class Headbutt(MeleeAttack):
    base_damage = (1, 8)
    name = "headbutt"

    def can_execute(self, actor, target):
        base_result = super().can_execute(actor, target)
        if not base_result:
            return base_result

        if actor.headbutt_cooldown > 0:
            return False

    def on_hit(self, actor, target):
        game = actor.game
        game.add_message(actor.name + " headbutts %s!" % target.name)
        super().on_hit(actor, target)
        actor.headbutt_cooldown = 20
        target.stunned = True


class Slice(MeleeAttack):
    base_damage = (4, 12)
    name = "headbutt"

    def on_hit(self, actor, target):
        game = actor.game
        game.add_message(actor.name + " slices %s!" % target.name)
        super().on_hit(actor, target)
