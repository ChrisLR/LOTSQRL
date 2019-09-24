import random

from lotsqrl import utils


class Action(object):
    name = ""

    def __init__(self, actor):
        self.actor = actor
        self.game = actor.game

    def can_execute(self, target):
        """
        Called when an action may be executed.
        Implementation is responsible for messages.
        :param target: The Targeted Actor
        :type target: lotsqrl.actors.base.Actor
        :return: Tells if an action is executable or not
        :rtype bool:
        """
        pass

    def execute(self, target):
        """
        Called when an action is executing.
        Implementation is responsible for messages.
        :param target: The Targeted Actor
        :type target: lotsqrl.actors.base.Actor
        :return: Tells if the action happened, a round elapses when True
        :rtype bool:
        """
        pass


class MeleeAttack(Action):
    base_damage = (1, 1)
    base_reach = 1

    def __init__(self, actor, damage=None, reach=None):
        super().__init__(actor)
        self.actor = actor
        self.damage = damage or self.base_damage
        self.reach = reach or self.base_reach

    def can_execute(self, target):
        distance = utils.get_distance(self.actor, target)
        if distance <= self.reach:
            return True
        return False

    def execute(self, target):
        # TODO This is where hit rolls would occur
        hit = True
        if hit:
            self.on_hit(target)
        else:
            self.on_miss(target)

        return True

    def on_hit(self, target):
        damage_min, damage_max = self.damage
        damage = random.randint(damage_min, damage_max)
        target.hp -= damage
        if target.hp <= 0:
            target.on_death()

    def on_miss(self, target):
        pass
