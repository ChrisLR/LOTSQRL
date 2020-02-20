import random

from lotsqrl import movement, tiles, selectors, utils
from lotsqrl.actions.base import MeleeAttack, TouchAction, Action
from lotsqrl.teams import ActorTypes, Team
from lotsqrl.messages import MessageScope


class Bite(MeleeAttack):
    base_damage = (1, 4)
    name = "bite"

    def on_hit(self, actor, target):
        game = actor.game
        game.messaging.add_scoped_message(
            message_actor=f"You bite {target.name}!",
            message_target=f"{actor.name} bites you!",
            message_others=f"{actor.name} bites {target.name}!",
            scope=MessageScope.TargetsPlayer,
            actor=actor, target=target
        )
        super().on_hit(actor, target)


class BurrowEgg(TouchAction):
    name = "burrow_egg"
    selectors = (
        selectors.TouchDirectional(
            "Press direction to burrow into a cocoon",
            filters=(selectors.filters.OnlyCocoons(),)
        ),
    )

    def can_execute(self, actor, target):
        base_result = super().can_execute(actor, target)
        if not base_result:
            return base_result

        if target.actor_type != ActorTypes.Cocoon or target.burrowed:
            return False

        return True

    def execute(self, actor, target):
        game = actor.game
        game.messaging.add_scoped_message(
            message_actor=f"You burrow into {target.name}!",
            message_target=f"{actor.name} burrows into you!",
            message_others=f"{actor.name} burrows into {target.name}!",
            actor=actor, target=target, scope=MessageScope.All
        )
        target.burrowed = True
        actor.level.remove_actor(actor)

        return True


class ConsumeMinion(TouchAction):
    name = "consume_minion"
    selectors = (
        selectors.TouchDirectional(
            "Press direction to consume minion",
            filters=(selectors.filters.OnlyAllies(),)
        ),
    )

    def can_execute(self, actor, target):
        base_result = super().can_execute(actor, target)
        if not base_result:
            actor.game.messaging.add_scoped_message(
                message_actor="There is no minion there.",
                actor=actor, scope=MessageScope.TargetsPlayer
            )
            return base_result

        if target.team != Team.SpiderQueen:
            actor.game.messaging.add_scoped_message(
                message_actor="You can only consume your own minions.",
                actor=actor, scope=MessageScope.TargetsPlayer
            )
            return False

        return True

    def execute(self, actor, target):
        if actor.score is not None:
            actor.score.corpses_eaten += 1

        actor.game.messaging.add_scoped_message(
            message_actor=f"You eat {target.name}!",
            message_target=f"{actor.name} eats you!",
            message_others=f"{actor.name} eats {target.name}!",
            actor=actor, target=target, scope=MessageScope.TargetsPlayer
        )
        actor.level.remove_actor(target)
        actor.target = None
        if actor.hp + self.heal <= actor.max_hp:
            actor.hp += self.heal
        else:
            actor.hp = actor.max_hp

        return True


class DevouringMaw(Bite):
    base_damage = (1, 4)
    name = "bite"

    def on_hit(self, actor, target):
        with utils.silence(actor.game):
            super().on_hit(actor, target)

        if target.hp <= 0:
            with utils.silence(actor.game):
                actor.actions.execute("eat_corpse", target=target.corpse)
            actor.game.messaging.add_scoped_message(
                message_actor=f"You devour {target.name} with one massive snap of your jaws!",
                message_target=f"{actor.name} devours you with one massive snap of its jaws!",
                message_others=f"{actor.name} devours {target.name} with one massive snap of its jaws!",
                actor=actor, target=target, scope=MessageScope.TargetsPlayer
            )
        else:
            actor.game.messaging.add_scoped_message(
                message_actor=f"You bite {target.name} with your oversized jaws!",
                message_target=f"{actor.name} bites you with its oversized jaws!",
                message_others=f"{actor.name} bites {target.name} with its oversized jaws!",
                actor=actor, target=target, scope=MessageScope.TargetsPlayer
            )


class EatCorpse(TouchAction):
    name = "eat_corpse"
    base_heal = 5
    selectors = (
        selectors.TouchDirectional(
            "Press direction to eat corpse",
            filters=(selectors.filters.OnlyCorpses(),)
        ),
    )

    def __init__(self, heal=None, reach=None):
        super().__init__(reach)
        self.heal = heal or self.base_heal

    def can_execute(self, actor, target):
        base_result = super().can_execute(actor, target)
        if not base_result:
            actor.game.messaging.add_scoped_message(
                message_actor="There is no edible corpse there.",
                actor=actor, scope=MessageScope.TargetsPlayer
            )
            return base_result

        if target.actor_type != ActorTypes.Corpse:
            return False

        return True

    def execute(self, actor, target):
        if actor.score is not None:
            actor.score.corpses_eaten += 1

        actor.game.messaging.add_scoped_message(
            message_actor=f"You eat {target.name}!",
            message_target=f"{actor.name} eats you!",
            message_others=f"{actor.name} eats {target.name}!",
            actor=actor, target=target, scope=MessageScope.TargetsPlayer
        )
        actor.level.remove_actor(target)
        actor.target = None
        if actor.hp + self.heal <= actor.max_hp:
            actor.hp += self.heal
        else:
            actor.hp = actor.max_hp

        evolution = actor.evolution
        if evolution is not None:
            evolution.consume(target)

        return True


class Jump(Action):
    base_cooldown = 6
    base_reach = 3
    name = "jump"

    def __init__(self, cooldown=None, reach=None):
        super().__init__(cooldown)
        self.reach = reach or self.base_reach
        self.selectors = (selectors.GridPointDirectional(self.reach, "Press direction to jump"),)

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
        messaging = game.messaging
        if level.get_tile(x, y) == tiles.CaveFloor:
            collides = level.get_actors_by_pos(x, y)
            collisions = [collide for collide in collides if collide is not self and collide.blocking]
            if collisions:
                collision_names = ','.join((collision.name for collision in collisions))
                messaging.add_scoped_message(
                    message_actor=f"You leap into {collision_names}!",
                    message_target=f"{actor.name} leaps into {collision_names}!",
                    message_others=f"{actor.name} leaps into {collision_names}!",
                    actor=actor, targets=collisions, scope=MessageScope.TargetsPlayer
                )

                dx, dy = utils.get_actor_delta(actor, collisions[0])
                dx = utils.sign(dx) * 2
                dy = utils.sign(dy) * 2

                for collision in collisions:
                    collision.hp -= random.randint(1, 3)
                    moved = movement.move_to(collision, collision.x + dx, collision.y + dy, bump=False)
                    if moved is False and collision is not game.boss:
                        messaging.add_scoped_message(
                            message_actor=f"You crush {collision.name} under you!",
                            message_target=f"You are crushed under {actor.name}!",
                            message_others=f"{collision.name} is crushed under {actor.name}!",
                            actor=actor, target=collision, scope=MessageScope.TargetsPlayer
                        )
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
        base_result = super().can_execute(actor, actor)
        if not base_result:
            return base_result

        return True

    def execute(self, actor, target):
        # TODO This is bad, do it better
        from lotsqrl.actors import Egg
        game = actor.game
        game.messaging.add_scoped_message(
            message_actor="You lay an egg.",
            message_others=f"{actor.name} lays an egg.",
            actor=actor, scope=MessageScope.TargetsPlayer
        )
        new_egg = Egg(actor.game, actor.x, actor.y)
        actor.level.add_actor(new_egg)
        actor.cooldowns.set(self.name, self.base_cooldown)
        if actor.score is not None:
            actor.score.eggs_laid += 1


class SpinCocoon(Action):
    base_cooldown = 20
    base_reach = 3
    name = "spin_cocoon"
    targets = 1

    def __init__(self, cooldown=None, reach=None):
        super().__init__(cooldown)
        self.reach = reach or self.base_reach
        self.target_line = None
        self.selectors = (
            selectors.LineDirectional(
                self.reach, "Press direction to spin a creature into a cocoon",
                (selectors.filters.OnlyEnemies(),)
            ),
        )

    def can_execute(self, actor, target):
        base_result = super().can_execute(actor, target)
        if not base_result:
            return base_result

        if target.team != Team.Goblin:
            actor.game.messaging.add_player_message("That wouldn't make a nutritious meal.", actor)
            return False

        dist = utils.get_distance(actor, target)
        if dist <= self.reach:
            target_line = utils.get_target_line(actor, target)
            obstacles = utils.get_obstacles_in_target_line(target_line)
            self.target_line = target_line
            if obstacles:
                return False

        return True

    def execute(self, actor, target):
        # TODO This is bad, do it better
        from lotsqrl.actors import Cocoon

        game = actor.game
        messaging = game.messaging
        level = actor.level
        if target == actor.game.boss:
            messaging.add_scoped_message(
                message_actor=f"You try to ensnare {target.name} in your web but it resists!",
                message_target=f"{actor.name} tries to ensnare you but you resist!",
                message_others=f"{actor.name} tries to ensnare {target.name} but it resists!",
                actor=actor, target=target, scope=MessageScope.TargetsPlayer
            )
        else:
            messaging.add_scoped_message(
                message_actor=f"You snatch {target.name} with your web, pulling and spinning it into a cocoon!",
                message_target=f"{actor.name} snatches you with its web, pulling and spinning you into a cocoon!",
                message_others=f"{actor.name} snatches {target.name} with its web, "
                               f"pulling and spinning it into a cocoon!",
                actor=actor, target=target, scope=MessageScope.TargetsPlayer
            )
            new_x, new_y = utils.get_closest_floor_in_line(self.target_line)
            target.dead = True
            level.remove_actor(target)
            level.add_actor(Cocoon(game, new_x, new_y))
            self.apply_cooldown(actor)
            if actor.score is not None:
                actor.score.webs_fired += 1

        return True


class SwallowWhole(TouchAction):
    name = "swallow_whole"
    selectors = (
        selectors.TouchDirectional(
            "Press direction to swallow your victim",
            filters=(selectors.filters.OnlyEnemies(),)
        ),
    )

    def can_execute(self, actor, target):
        base_result = super().can_execute(actor, target)
        if not base_result:
            actor.game.messaging.add_scoped_message(
                message_actor="There is no enemy there.",
                actor=actor, scope=MessageScope.TargetsPlayer
            )
            return base_result

        evolution = actor.evolution.get("Swallow Whole")
        if not evolution:
            actor.game.messaging.add_scoped_message(
                message_actor="You cannot do that",
                actor=actor, scope=MessageScope.TargetsPlayer
            )
            return False

        # TODO Must make sure actor is not already digesting someone

        return True

    def execute(self, actor, target):
        # TODO Implement the action
        pass
