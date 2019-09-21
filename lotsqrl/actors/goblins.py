import random

from lotsqrl import movement, utils
from lotsqrl.actors.base import Actor
from lotsqrl.teams import Team, ActorTypes


class Goblin(Actor):
    actor_type = ActorTypes.Goblin
    ascii_color = 'green'

    def __init__(self, game, x, y):
        super().__init__(game, 5, "g", "Goblin", x, y, team=Team.Goblin)
        self.display_priority = 8

    def act(self):
        if self.stunned > 0:
            self.stunned -= 1
            return

        if not self.dead:
            spiders = self.level.get_actors_by_team(Team.SpiderQueen)
            if spiders:
                closest_spider = utils.get_closest_actor(self, spiders)
                return movement.step_to_target(self, closest_spider)

    def bump(self, target):
        if not target.team == Team.Goblin:
            return self.stab(target)
        return False

    def stab(self, target):
        self.game.add_message(self.name + " stabs %s!" % target.name)
        damage = random.randint(1, 4)
        target.hp -= damage
        if target.hp <= 0:
            target.on_death()

        return True


class GoblinChief(Actor):
    actor_types = ActorTypes.GoblinChief
    ascii_color = 'green'

    def __init__(self, game, x, y):
        super().__init__(game, 50, "G", "Goblin Chief", x, y, team=Team.Goblin)
        self.display_priority = 7
        self.headbutt_cooldown = 0

    def act(self):
        if self.stunned > 0:
            self.stunned -= 1
            return

        if self.headbutt_cooldown > 1:
            self.headbutt_cooldown -= 1

        if not self.dead:
            spiders = self.level.get_actors_by_team(Team.SpiderQueen)
            if spiders:
                closest_spider = utils.get_closest_actor(self, spiders)
                return movement.step_to_target(self, closest_spider)

    def bump(self, target):
        if target.team != Team.SpiderQueen:
            return False

        if self.headbutt_cooldown == 0:
            return self.headbutt(target)
        return self.slice(target)

    def headbutt(self, target):
        self.game.add_message(self.name + " headbutts %s!" % target.name)
        damage = random.randint(1, 8)
        self.headbutt_cooldown = 20
        target.hp -= damage
        if target.hp <= 0:
            target.on_death()
        target.stunned = True

        return True

    def slice(self, target):
        self.game.add_message(self.name + " slices %s!" % target.name)
        damage = random.randint(4, 12)
        target.hp -= damage
        if target.hp <= 0:
            target.on_death()

        return True
