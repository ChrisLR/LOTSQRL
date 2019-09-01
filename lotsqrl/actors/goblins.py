import random

from lotsqrl.actors.base import Actor
from lotsqrl.teams import Team


class Goblin(Actor):
    def __init__(self, x, y):
        super().__init__(5, "g", "Goblin", x, y, team=Team.Goblin)
        self.display_priority = 8

    def act(self):
        if self.stunned > 0:
            self.stunned -= 1
            return

        if not self.dead:
            spiders = [actor for actor in self.level.actors
                       if actor.team == Team.QueenSpider and not actor.dead]
            if spiders:
                closest_spider = get_closest_actor(self, spiders)
                return step_to_target(self, closest_spider)

    def bump(self, target):
        if not isinstance(target, GoblinChief):
            return self.stab(target)
        return True

    def stab(self, target):
        messages.append(self.name + " stabs %s!" % target.name)
        damage = random.randint(1, 4)
        target.hp -= damage
        if target.hp <= 0:
            target.on_death()

        return True


class GoblinChief(Actor):
    def __init__(self, x, y):
        super().__init__(50, "G", "Goblin Chief", x, y, team=Team.Goblin)
        self.display_priority = 7
        self.headbutt_cooldown = 0

    def act(self):
        if self.stunned > 0:
            self.stunned -= 1
            return

        if self.headbutt_cooldown > 1:
            self.headbutt_cooldown -= 1

        if not self.dead:
            spiders = [actor for actor in self.level.actors
                       if actor.team == Team.QueenSpider and not actor.dead]
            if spiders:
                closest_spider = get_closest_actor(self, spiders)
                return step_to_target(self, closest_spider)

    def bump(self, target):
        if self.headbutt_cooldown == 0:
            return self.headbutt(target)
        return self.slice(target)

    def headbutt(self, target):
        messages.append(self.name + " headbutts %s!" % target.name)
        damage = random.randint(1, 8)
        self.headbutt_cooldown = 20
        target.hp -= damage
        if target.hp <= 0:
            target.on_death()
        target.stunned = True

        return True

    def slice(self, target):
        messages.append(self.name + " slices %s!" % target.name)
        damage = random.randint(4, 12)
        target.hp -= damage
        if target.hp <= 0:
            target.on_death()

        return True
