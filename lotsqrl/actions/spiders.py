import random

from lotsqrl import movement, tiles, utils
from lotsqrl.actions.base import MeleeAttack, TouchAction, Action
from lotsqrl.teams import ActorTypes


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
        actor.game.add_message("%s burrows into %s!" % (actor.name, target.name))
        target.burrowed = True
        actor.level.remove_actor(actor)

        return True


class EatCorpse(TouchAction):
    name = "eat_corpse"
    base_heal = 5

    def __init__(self, heal=None, reach=None):
        super().__init__(reach)
        self.heal = heal or self.base_heal

    def can_execute(self, actor, target):
        base_result = super().can_execute(actor, target)
        if not base_result:
            return base_result

        if target.actor_type != ActorTypes.Corpse:
            return False

        return True

    def execute(self, actor, target):
        if actor.score is not None:
            actor.score.corpses_eaten += 1

        if actor.is_player:
            actor.game.add_message("You eat %s !" % target.name)
        else:
            actor.game.add_message("%s eats %s !" % (actor.name, target.name))
        actor.level.remove_actor(target)
        actor.target = None
        if actor.hp + self.heal <= actor.max_hp:
            actor.hp += self.heal
        else:
            actor.hp = actor.max_hp

        return True


class Jump(Action):
    base_cooldown = 6
    base_reach = 3
    name = "jump"

    def __init__(self, cooldown=None, reach=None):
        super().__init__(cooldown)
        self.reach = reach or self.base_reach

    def can_execute(self, actor, target):
        base_result = super().can_execute(actor, target)
        if not base_result:
            return base_result

        if utils.get_distance(actor, target) > self.reach:
            return False

        if not utils.has_clear_line_of_sight(actor, target):
            return False

        return True

    def execute(self, actor, target):
        x, y = target.x, target.y
        level = actor.level
        game = actor.game
        if level.get_tile(x, y) == tiles.CaveFloor:
            collides = level.get_actors_by_pos(x, y)
            collisions = [collide for collide in collides if collide is not self and collide.blocking]
            if collisions:
                game.add_message("%s leaps into %s" % (actor.name, ','.join((collision.name for collision in collisions))))
                dx, dy = utils.get_actor_delta(actor, collisions[0])
                dx = utils.sign(dx) * 2
                dy = utils.sign(dy) * 2

                for collision in collisions:
                    collision.hp -= random.randint(1, 3)
                    moved = movement.move_to(collision, collision.x + dx, collision.y + dy, bump=False)
                    if moved is False and collision is not game.boss:
                        game.add_message("%s is crushed under %s!" % (collision.name, actor.name))
                        collision.on_death()
                        if actor.score is not None:
                            actor.score.enemies_crushed += 1

            actor.x = x
            actor.y = y
            actor.cooldowns.set(self.name, self.cooldown)
        else:
            return False


class LayEgg(Action):
    base_cooldown = 10
    name = "lay_egg"

    def can_execute(self, actor, target):
        base_result = super().can_execute(actor, target)
        if not base_result:
            return base_result

        return True

    def execute(self, actor, target):
        # TODO This is bad, do it better
        from lotsqrl.actors import Egg
        actor.game.add_message("%s lays an egg." % actor.name)
        new_egg = Egg(actor.game, actor.x, actor.y)
        actor.level.add_actor(new_egg)
        actor.cooldowns.set(self.name, self.base_cooldown)
        if actor.score is not None:
            actor.score.eggs_laid += 1
