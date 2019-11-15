import random

from lotsqrl import utils


class Action(object):
    base_cooldown = 0
    name = ""

    def __init__(self, cooldown=None):
        self.cooldown = cooldown or self.base_cooldown

    def apply_cooldown(self, actor):
        actor.cooldowns.set(self.name)

    def can_execute(self, actor, target):
        """
        Called when an action may be executed.
        Implementation is responsible for messages.
        :param actor: The Executing Actor
        :type actor: lotsqrl.actors.base.Actor
        :param target: The Targeted Actor
        :type target: lotsqrl.actors.base.Actor
        :return: Tells if an action is executable or not
        :rtype bool:
        """
        cooldown = actor.cooldowns.get(self.name)
        if cooldown:
            actor.game.player_message(actor, "You need to wait %s more rounds." % cooldown)
            return False
        return True

    def execute(self, actor, target):
        """
        Called when an action is executing.
        Implementation is responsible for messages.
        :param actor: The Executing Actor
        :type actor: lotsqrl.actors.base.Actor
        :param target: The Targeted Actor
        :type target: lotsqrl.actors.base.Actor
        :return: Tells if the action happened, a round elapses when True
        :rtype bool:
        """
        pass


class MeleeAttack(Action):
    base_damage = (1, 1)
    base_reach = 1

    def __init__(self, damage=None, reach=None):
        super().__init__()
        self.damage = damage or self.base_damage
        self.reach = reach or self.base_reach

    def can_execute(self, actor, target):
        distance = utils.get_distance(actor, target)
        if distance <= self.reach:
            return True
        return False

    def execute(self, actor, target):
        # TODO This is where hit rolls would occur
        hit = True
        if hit:
            self.on_hit(actor, target)
        else:
            self.on_miss(actor, target)

        return True

    def on_hit(self, actor, target):
        damage_min, damage_max = self.damage
        damage = random.randint(damage_min, damage_max)
        target.hp -= damage
        if target.hp <= 0:
            target.on_death()
            if actor.score is not None:
                actor.score.kills += 1

    def on_miss(self, actor, target):
        pass


class TouchAction(Action):
    base_reach = 1

    def __init__(self, reach=None):
        super().__init__()
        self.reach = reach or self.base_reach

    def can_execute(self, actor, target):
        distance = utils.get_distance(actor, target)
        if distance <= self.reach:
            return True
        return False

    def execute(self, actor, target):
        return True
