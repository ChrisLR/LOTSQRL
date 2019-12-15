from lotsqrl.actions.base import MeleeAttack
from lotsqrl.messages import MessageScope


class Stab(MeleeAttack):
    base_damage = (1, 4)
    name = "stab"

    def on_hit(self, actor, target):
        game = actor.game
        game.messaging.add_scoped_message(
            message_actor=f"You stab {target.name}!",
            message_target=f"{actor.name} stabs you!",
            message_others=f"{actor.name} stabs {target.name}!",
            actor=actor, target=target, scope=MessageScope.TargetsPlayer
        )
        super().on_hit(actor, target)


class Headbutt(MeleeAttack):
    base_damage = (1, 8)
    base_cooldown = 20
    name = "headbutt"

    def can_execute(self, actor, target):
        base_result = super().can_execute(actor, target)
        if not base_result:
            return base_result

    def on_hit(self, actor, target):
        game = actor.game
        game.messaging.add_scoped_message(
            message_actor=f"You headbutt {target.name}!",
            message_target=f"{actor.name} headbutts you!",
            message_others=f"{actor.name} headbutts {target.name}!",
            actor=actor, target=target, scope=MessageScope.TargetsPlayer
        )
        super().on_hit(actor, target)
        self.apply_cooldown(actor)
        target.stunned = True


class Slice(MeleeAttack):
    base_damage = (4, 12)
    name = "headbutt"

    def on_hit(self, actor, target):
        game = actor.game
        game.messaging.add_scoped_message(
            message_actor=f"You slice {target.name}!",
            message_target=f"{actor.name} slices you!",
            message_others=f"{actor.name} slices {target.name}!",
            actor=actor, target=target, scope=MessageScope.TargetsPlayer
        )
        super().on_hit(actor, target)
