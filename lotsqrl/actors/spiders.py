import random
import sys
import time

from bearlibterminal import terminal

from lotsqrl import behaviors, movement, utils
from lotsqrl.actors.base import Actor
from lotsqrl.scenes.helpfile import draw_help_file
from lotsqrl.score import Score
from lotsqrl.teams import Team, ActorTypes


class Egg(Actor):
    actor_type = ActorTypes.Egg

    def __init__(self, game, x, y):
        super().__init__(game, 1, "0", "Egg", x, y, team=Team.SpiderQueen)
        self.hatch_countdown = 10
        self.display_priority = 9

    def act(self):
        if self.dead or self.level is None:
            return

        self.hatch_countdown -= 1
        if self.hatch_countdown <= 0:
            self.level.add_actor(Spiderling(self.game, self.x, self.y))
            self.level.remove_actor(self)


class Cocoon(Actor):
    actor_type = ActorTypes.Cocoon

    def __init__(self, game, x, y):
        super().__init__(game, 1, "(", "Cocoon", x, y, team=Team.SpiderQueen)
        self.hatch_countdown = 10
        self.display_priority = 9
        self.burrowed = False

    def act(self):
        if self.dead or self.level is None:
            return

        if self.burrowed is True:
            self.hatch_countdown -= 1
            if self.hatch_countdown <= 0:
                self.level.add_actor(Spider(self.game, self.x, self.y))
                self.level.remove_actor(self)


class Arachnid(Actor):
    bite_damage_range = (1, 4)

    def bite(self, target):
        if target.team == self.team:
            return False

        if self.is_player:
            self.game.add_message("You bite %s!" % target.name)
        else:
            self.game.add_message("%s bites %s!" % (self.name, target.name))
        damage = random.randint(*self.bite_damage_range)
        target.hp -= damage
        if target.hp <= 0:
            target.on_death()
            if self.score is not None:
                self.score.kills += 1

        return True

    def burrow(self, target):
        pass

    def eat(self, target):
        if self.score is not None:
            self.score.corpses_eaten += 1

        if self.is_player:
            self.game.add_message("You eat %s !" % target.name)
        else:
            self.game.add_message("%s eats %s !" % (self.name, target.name))
        self.level.remove_actor(target)
        self.target = None
        if self.hp + 5 <= self.max_hp:
            self.hp += 5
        else:
            self.hp = self.max_hp

        return True


class Spiderling(Arachnid):
    actor_type = ActorTypes.Spiderling
    behaviors = [behaviors.Attack, behaviors.BurrowIntoCocoon, behaviors.EatCorpse]
    bite_damage_range = (1, 4)

    def __init__(self, game, x, y):
        super().__init__(game, 4, "s", "Spiderling", x, y, team=Team.SpiderQueen)
        self.target = None
        self.display_priority = 8
        self.max_hp = 8

    def act(self):
        if self.stunned > 0:
            self.stunned -= 1
            return

        if self.dead or self.level is None:
            return

        next_behavior = min(self.behaviors, key=lambda b: b.get_priority(self))
        return next_behavior.execute(self)

    def bump(self, target):
        if target.actor_type == ActorTypes.Cocoon and not target.burrowed:
            return self.burrow(target)

        if target is self.target or target.team == Team.Goblin:
            if target.dead:
                return self.eat(target)
            else:
                return self.bite(target)

        return False

    def burrow(self, target):
        self.game.add_message("%s burrows into %s!" % (self.name, target.name))
        target.burrowed = True
        self.level.remove_actor(self)
        return True


class Spider(Arachnid):
    actor_type = ActorTypes.Spider
    behaviors = [behaviors.Attack, behaviors.EatCorpse]
    bite_damage_range = (2, 8)

    def __init__(self, game, x, y):
        super().__init__(game, 10, "S", "Spider", x, y, team=Team.SpiderQueen)
        self.target = None
        self.display_priority = 8
        self.max_hp = 20

    def act(self):
        if self.stunned > 0:
            self.stunned -= 1
            return

        if self.dead or self.level is None:
            return

        next_behavior = min(self.behaviors, key=lambda b: b.get_priority(self))
        return next_behavior.execute(self)

    def bump(self, target):
        if target is self.target or target.team == Team.Goblin:
            if target.dead:
                return self.eat(target)
            else:
                return self.bite(target)

        return False


class SpiderQueen(Arachnid):
    actor_type = ActorTypes.SpiderQueen
    bite_damage_range = (4, 8)
    egg_delay = 11
    jump_delay = 6
    web_delay = 20

    def __init__(self, game, x, y):
        super().__init__(game, 20, "@", "You", x, y, team=Team.SpiderQueen)
        self.egg_cool_down = 0
        self.jump_cool_down = 0
        self.web_cooldown = 0
        self.is_player = True
        self.score = Score()
        self.moved = False
        self.display_priority = 1
        self.max_hp = 40

    def act(self):
        if self.stunned > 0:
            self.stunned -= 1
            self.moved = True
            return

        if self.dead or self.level is None:
            return

        press = terminal.read()
        move_action = movement.move_actions.get(press)
        if move_action is not None:
            self.moved = move_action(self)

        if press == terminal.TK_E:
            self.moved = self.try_eat()
        elif press == terminal.TK_L:
            self.moved = self.lay_egg()
        elif press == terminal.TK_J:
            self.moved = self.jump()
        elif press == terminal.TK_KP_5:
            self.moved = True
        elif press == terminal.TK_F:
            self.moved = self.fire_web()
        elif press == terminal.TK_CLOSE:
            sys.exit()
        elif press == terminal.TK_F1:
            draw_help_file()
        elif press == terminal.TK_ESCAPE:
            if self.game.game_won:
                self.game.should_restart = True
                return

        if self.moved:
            if self.egg_cool_down > 0:
                self.egg_cool_down -= 1
            if self.jump_cool_down > 0:
                self.jump_cool_down -= 1
            if self.web_cooldown > 0:
                self.web_cooldown -= 1

    def bump(self, target):
        return self.bite(target)

    def fire_web(self):
        if self.web_cooldown > 0:
            self.game.add_message("You need to wait %s more rounds to fire web." % self.web_cooldown)
            return False

        self.game.add_message("Press direction to fire web", show_now=True)
        offset = utils.get_directional_pos()
        if offset is None:
            self.game.add_message("Cancelled", show_now=True)
            return False

        if self.score is not None:
            self.score.webs_fired += 1
        self.web_cooldown = 20

        for i in range(10):
            web_x, web_y = self.x + (offset[0] * i), self.y + (offset[1] * i)
            if self.level.get_tile(web_x, web_y) == "#":
                self.game.add_message("Your web hits a wall, press a key to fling yourself.", show_now=True)
                offset = utils.get_directional_pos()
                if offset is None:
                    self.game.add_message("You snap your web with your fangs")
                    return True
                for wf in range(1, 5):
                    gx, gy = self.x + (offset[0] * wf), self.y + (offset[1] * wf)
                    actors = [actor for actor in self.level.get_actors_by_pos(gx, gy) if not actor.dead]
                    if actors:
                        actor = actors[0]
                        self.game.add_message("You smash against %s!" % actor.name)
                        actor.stunned = 2
                        self.x = gx - offset[0]
                        self.y = gy - offset[1]
                        self.hp -= random.randint(1, 4)
                        actor.hp -= random.randint(2, 8)
                        if self.hp < 0:
                            self.on_death()
                        if actor.hp < 0:
                            actor.on_death()
                        break
                    else:
                        tile = self.level.get_tile(gx, gy)
                        if tile == "#":
                            self.x = gx - offset[0]
                            self.y = gy - offset[1]
                            break
                else:
                    self.x = gx
                    self.y = gy
                return True

            web_char = utils.direction_offsets_char.get(offset)
            terminal.layer(2)
            # TODO Improve this way to draw something/animation now
            camera = self.game.camera
            camera.set_sprite_font()
            terminal.put(*camera.transform(web_x, web_y), web_char)
            camera.reset_font()
            terminal.layer(3)
            terminal.refresh()
            time.sleep(0.05)
            goblins = self.level.get_actors_by_pos(web_x, web_y, team=Team.Goblin)
            if goblins:
                goblin = goblins[0]
                if goblin is None:
                    continue
                self.game.add_message("You web latches on %s!" % goblin.name)
                self.game.add_message("Press direction to fling %s" % goblin.name, show_now=True)
                offset = utils.get_directional_pos()
                if offset is None:
                    self.game.add_message("You snap your web with your fangs")
                    return True
                self.game.add_message("You fling %s in the air!" % goblin.name)
                for wf in range(1, 5):
                    gx, gy = goblin.x + (offset[0] * wf), goblin.y + (offset[1] * wf)
                    actors = [actor for actor in self.level.get_actors_by_pos(gx, gy) if not actor.dead]
                    if actors:
                        actor = actors[0]
                        if actor == self and goblin != self.game.boss:
                            self.game.add_message("You catch %s and start spinning a cocoon!" % goblin.name)
                            goblin.dead = True
                            self.level.remove_actor(goblin)
                            new_cocoon = Cocoon(self.game, gx - offset[0], gy - offset[1])
                            self.level.add_actor(new_cocoon)
                            return True
                        self.game.add_message("%s smashes against %s!" % (goblin.name, actor.name))
                        goblin.stunned = 1
                        if actor != self.game.player:
                            actor.stunned = 1
                        goblin.x = gx - offset[0]
                        goblin.y = gy - offset[1]
                        goblin.hp -= random.randint(1, 4)
                        actor.hp -= random.randint(1, 4)
                        if goblin.hp < 0:
                            goblin.on_death()
                        if actor.hp < 0:
                            actor.on_death()
                        break
                    else:
                        tile = self.level.get_tile(gx, gy)
                        if tile == "#":
                            self.game.add_message("%s smashes against the wall!" % goblin.name)
                            goblin.stunned = 3
                            goblin.hp -= random.randint(4, 8)
                            if goblin.hp < 0:
                                goblin.on_death()
                            goblin.x = gx - offset[0]
                            goblin.y = gy - offset[1]
                            break
                else:
                    goblin.x = gx
                    goblin.y = gy

                return True
        else:
            self.game.add_message("There is no one to web there.")

        return False

    def lay_egg(self):
        if self.egg_cool_down > 0:
            self.game.add_message("You need to wait %s more rounds to lay." % self.egg_cool_down)
            return False

        self.game.add_message("You lay an egg.")
        new_egg = Egg(self.game, self.x, self.y)
        self.level.add_actor(new_egg)
        self.egg_cool_down = self.egg_delay
        if self.score is not None:
            self.score.eggs_laid += 1

        return True

    def jump(self):
        if self.jump_cool_down > 0:
            self.game.add_message("You need to wait %s more rounds to jump." % self.jump_cool_down)
            return False

        self.game.add_message("Press direction to jump", show_now=True)
        offset = utils.get_directional_pos()
        if offset is None:
            self.game.add_message("Cancelled", show_now=True)
            return False

        ox, oy = offset
        if ox != 0:
            ox *= 3
        if oy != 0:
            oy *= 3

        jumped = self.jump_to(self.x + ox, self.y + oy)
        if jumped is False:
            self.game.add_message("Can't jump there, a wall in the way.")
            return False
        else:
            self.jump_cool_down = self.jump_delay
            return True

    def try_eat(self):
        self.game.add_message("Press direction to eat corpse", show_now=True)
        offset = utils.get_directional_pos()
        if offset is None:
            self.game.add_message("Cancelled", show_now=True)
            return False

        tx, ty = self.x + offset[0], self.y + offset[1]
        targets = self.level.get_actors_by_pos(tx, ty, team=Team.Corpse)
        if targets:
            return self.eat(targets[0])

        self.game.add_message("No corpses there.", show_now=True)
        return False

    def on_death(self):
        self.blocking = False
        self.dead = True
        self.display_char = "%"
        self.game.add_message("You are DEAD!")

    def jump_to(self, x, y):
        if self.level.get_tile(x, y) == ".":
            collides = self.level.get_actors_by_pos(x, y)
            collisions = [collide for collide in collides if collide is not self and collide.blocking]
            if collisions:
                self.game.add_message("You leap into %s" % ','.join((collision.name for collision in collisions)))
                dx, dy = utils.get_actor_delta(self, collisions[0])
                dx = utils.sign(dx) * 2
                dy = utils.sign(dy) * 2

                for collision in collisions:
                    collision.hp -= random.randint(1, 3)
                    moved = movement.move_to(collision, collision.x + dx, collision.y + dy, bump=False)
                    if moved is False and collision is not self.game.boss:
                        self.game.add_message("%s is crushed under you!" % collision.name)
                        collision.on_death()
                        if self.score is not None:
                            self.score.enemies_crushed += 1

            self.x = x
            self.y = y
        else:
            return False
