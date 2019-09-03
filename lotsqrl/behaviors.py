from enum import IntEnum

from lotsqrl import utils, movement
from lotsqrl.teams import Team, ActorTypes


class Priority(IntEnum):
    Extreme = 1
    High = 2
    Medium = 3
    Low = 4
    VeryLow = 5
    Never = 6


class Behavior(object):
    def execute(self, actor):
        pass

    def get_priority(self, actor):
        pass


class Attack(Behavior):
    @classmethod
    def execute(cls, actor, target=None):
        if target is None:
            target = cls._get_target(actor)
            if target is None:
                return False

        dist = utils.get_distance(actor, target)
        if dist <= 1:
            return actor.bite(target)
        else:
            return movement.step_to_target(actor, target)

    @classmethod
    def _get_target(cls, actor):
        goblins = actor.level.get_actors_by_team(Team.Goblin)
        if not goblins:
            return None

        goblin = utils.get_closest_actor(actor, goblins)

        return goblin

    @classmethod
    def get_priority(cls, actor):
        goblins = actor.level.get_actors_by_team(Team.Goblin)
        if not goblins:
            return Priority.Never

        goblin = utils.get_closest_actor(actor, goblins)
        dist = utils.get_distance(actor, goblin)
        if dist <= 1:
            return Priority.Extreme
        elif dist == 2:
            return Priority.High
        else:
            return Priority.Low


class BurrowIntoCocoon(Behavior):
    @classmethod
    def execute(cls, actor, target=None):
        if target is None:
            target = cls._get_target(actor)
            if target is None:
                return False

        dist = utils.get_distance(actor, target)
        if dist <= 1:
            return actor.burrow(target)
        else:
            return movement.step_to_target(actor, target)

    @classmethod
    def _get_target(cls, actor):
        spiders = actor.level.get_actors_by_team(Team.SpiderQueen)
        cocoons = [c for c in spiders if c.actor_type == ActorTypes.Cocoon and c.burrowed is False]
        if not cocoons:
            return None

        cocoon = utils.get_closest_actor(actor, cocoons)

        return cocoon

    @classmethod
    def get_priority(cls, actor):
        if cls._get_target(actor):
            return Priority.Medium
        else:
            return Priority.Never


class EatCorpse(Behavior):
    @classmethod
    def execute(cls, actor, target=None):
        if target is None:
            target = cls._get_target(actor)
            if target is None:
                return False

        dist = utils.get_distance(actor, target)
        if dist <= 1:
            return actor.eat(target)
        else:
            return movement.step_to_target(actor, target)

    @classmethod
    def _get_target(cls, actor):
        corpses = actor.level.get_actors_by_team(Team.Corpse)
        if not corpses:
            return None

        target = utils.get_closest_actor(actor, corpses)

        return target

    @classmethod
    def get_priority(cls, actor):
        """
        Priority is based on health but adjusted when corpses are close
        """
        if actor.hp >= actor.max_hp:
            return Priority.Never

        corpses = actor.level.get_actors_by_team(Team.Corpse)
        if not corpses:
            return Priority.Never

        closest_corpse = utils.get_closest_actor(actor, corpses)
        dist = utils.get_distance(actor, closest_corpse)

        hp = actor.hp
        quarter_hp = actor.max_hp / 4
        if hp >= quarter_hp * 3:
            if dist <= 1:
                return Priority.Medium
            else:
                return Priority.VeryLow
        elif hp >= quarter_hp * 2:
            if dist <= 1:
                return Priority.High
            elif dist <= 3:
                return Priority.Medium
            else:
                return Priority.Low
        else:
            return Priority.High
