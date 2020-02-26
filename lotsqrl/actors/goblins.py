from lotsqrl import actions, movement, utils
from lotsqrl.actors.base import Actor
from lotsqrl.teams import Team, ActorTypes


class Goblin(Actor):
    actor_type = ActorTypes.Goblin
    base_actions = (actions.Stab(),)

    def __init__(self, game, x, y):
        super().__init__(game, 5, "Goblin", x, y, team=Team.Goblin, ascii_char="g", ascii_color="green")
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
            return self.actions.try_execute("stab", target)
        return False


class GoblinChief(Actor):
    actor_types = ActorTypes.GoblinChief
    base_actions = (actions.Headbutt(), actions.Slice(),)

    def __init__(self, game, x, y):
        super().__init__(game, 50, "Goblin Chief", x, y, team=Team.Goblin, ascii_char="G", ascii_color="green")
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
            return self.actions.try_execute("headbutt", target)
        return self.actions.try_execute("slice", target)

    def on_death(self, leave_corpse=True):
        self.game.messaging.add_system_message("The boss has been killed!")
        super().on_death(leave_corpse=leave_corpse)
