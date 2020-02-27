from lotsqrl import actions, behaviors, components, controllers, evolutions, inputmap
from lotsqrl.actors.base import Actor
from lotsqrl.score import Score
from lotsqrl.teams import Team, ActorTypes


class Egg(Actor):
    actor_type = ActorTypes.Egg
    default_controller = controllers.NullController

    def __init__(self, game, x, y):
        super().__init__(game, 1, "Egg", x, y, team=Team.SpiderQueen, ascii_char="0")
        self.hatch_countdown = 10
        self.display_priority = 9

    def act(self):
        if self.dead or self.level is None:
            return

        # TODO This is better as a status effect, not an "ACT"
        self.hatch_countdown -= 1
        if self.hatch_countdown <= 0:
            self.level.add_actor(Spiderling(self.game, self.x, self.y))
            self.level.remove_actor(self)


class Cocoon(Actor):
    actor_type = ActorTypes.Cocoon
    ascii_color = '#7fffd4'
    default_controller = controllers.NullController

    def __init__(self, game, x, y):
        super().__init__(game, 1, "Cocoon", x, y, team=Team.SpiderQueen, ascii_char="(")
        self.hatch_countdown = 10
        self.display_priority = 9
        self.burrowed = False

    def act(self):
        if self.dead or self.level is None:
            return

        # TODO This is better as a status effect, not an "ACT"
        if self.burrowed is True:
            self.hatch_countdown -= 1
            if self.hatch_countdown <= 0:
                self.level.add_actor(Spider(self.game, self.x, self.y))
                self.level.remove_actor(self)


class Arachnid(Actor):
    ascii_color = "red"
    base_actions = (actions.Bite(), actions.EatCorpse())
    bite_damage_range = (1, 4)

    def __init__(self, game, hp, name="", x=0, y=0, team=None,
                 ascii_char="s", ascii_color="red", tile_char=None):
        super().__init__(game, hp, name, x, y, team, ascii_char, ascii_color, tile_char)
        self.evolution = components.Evolution(self, None)


class Spiderling(Arachnid):
    actor_type = ActorTypes.Spiderling
    base_actions = (actions.Bite(), actions.BurrowEgg(), actions.EatCorpse())
    behaviors = [behaviors.Attack, behaviors.BurrowIntoCocoon, behaviors.EatCorpse]

    def __init__(self, game, x, y):
        super().__init__(game, 4, "Spiderling", x, y, team=Team.SpiderQueen)
        self.target = None
        self.display_priority = 8
        self.max_hp = 8

    def bump(self, target):
        if target.actor_type == ActorTypes.Cocoon and not target.burrowed:
            return self.actions.try_execute("burrow_egg", target)

        if target is self.target or target.team == Team.Goblin:
            if not target.dead:
                return self.actions.try_execute("bite", target)

        return False


class Spider(Arachnid):
    actor_type = ActorTypes.Spider
    base_actions = (actions.Bite(damage=(2, 8)), actions.EatCorpse(), actions.Jump())
    behaviors = [behaviors.Attack, behaviors.EatCorpse, behaviors.JumpOnEnemy]

    def __init__(self, game, x, y):
        super().__init__(game, 10, "Spider", x, y, team=Team.SpiderQueen, ascii_char="S")
        self.target = None
        self.display_priority = 8
        self.max_hp = 20

    def bump(self, target):
        if target is self.target or target.team == Team.Goblin:
            if not target.dead:
                return self.actions.try_execute("bite", target)

        return False


class SpiderQueen(Arachnid):
    actor_type = ActorTypes.SpiderQueen
    base_actions = (
        actions.Bite(damage=(4, 8)),
        actions.EatCorpse(),
        actions.Jump(),
        actions.LayEgg(),
        actions.SpinCocoon(),
    )
    input_map = inputmap.SpiderQueen
    web_delay = 20

    def __init__(self, game, x, y):
        # TODO The string for ascii mode must not be the same as the one for the graphics.
        # TODO The @ must be assigned to the player, no matter what it is controlling
        # TODO We will need two seperate tilesets
        super().__init__(game, 20, "Spider Queen", x, y, team=Team.SpiderQueen, ascii_char="@")
        self.evolution = components.Evolution(self, evolutions.create_spider_queen_evolution())
        self.is_player = True
        self.score = Score()
        self.moved = False
        self.display_priority = 1
        self.max_hp = 40

    def bump(self, target):
        if target.team == Team.Goblin:
            return self.actions.try_execute("bite", target)
