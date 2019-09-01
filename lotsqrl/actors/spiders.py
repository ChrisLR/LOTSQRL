import random
import sys
import time

from bearlibterminal import terminal

from lotsqrl.actors.base import Actor
from lotsqrl.teams import Team
from lotsqrl import movement, utils
from lotsqrl.scenes.helpfile import draw_help_file


class Egg(Actor):
    def __init__(self, game, x, y):
        super().__init__(game, 1, "0", "Egg", x, y, team=Team.QueenSpider)
        self.hatch_countdown = 10
        self.display_priority = 9

    def act(self):
        if self.dead:
            return

        self.hatch_countdown -= 1
        if self.hatch_countdown <= 0:
            self.level.add_actor(Spiderling(self.game, self.x, self.y))
            self.level.remove_actor(self)


class Cocoon(Actor):
    def __init__(self, game, x, y):
        super().__init__(game, 1, "(", "Cocoon", x, y, team=Team.QueenSpider)
        self.hatch_countdown = 10
        self.display_priority = 9
        self.burrowed = False

    def act(self):
        if self.dead:
            return

        if self.burrowed is True:
            self.hatch_countdown -= 1
            if self.hatch_countdown <= 0:
                self.level.add_actor(Spider(self.game, self.x, self.y))
                self.level.remove_actor(self)


class Spiderling(Actor):
    def __init__(self, game, x, y):
        super().__init__(game, 4, "s", "Spiderling", x, y, team=Team.QueenSpider)
        self.target = None
        self.display_priority = 8
        self.max_hp = 8

    def act(self):
        if self.stunned > 0:
            self.stunned -= 1
            return

        if self.dead:
            return

        if self.target is None or self.target.level is None:
            targets = [actor for actor in self.level.actors
                       if actor.team == Team.Goblin
                       or (isinstance(actor, Cocoon) and not actor.burrowed)]
            if not targets:
                spider = next(actor for actor in self.level.actors if actor.is_player)
                return movement.step_to_target(self, spider)
            target = utils.get_closest_actor(self, targets)
            if target.dead:
                dist = utils.get_distance(self, target)
                if dist <= 1:
                    return self.eat(target)
                else:
                    return movement.step_to_target(self, target)
            return movement.step_to_target(self, target)
        else:
            dist = utils.get_distance(self, self.target)
            if dist <= 1:
                return self.eat(self.target)
            else:
                return movement.step_to_target(self, self.target)

    def bump(self, target):
        if isinstance(target, Cocoon):
            self.game.add_message("%s burrows into %s!" % (self.name, target.name))
            target.burrowed = True
            self.level.remove_actor(self)
            return True

        if target is self.target or target.team == Team.Goblin:
            if target.dead:
                return self.eat(target)
            else:
                return self.bite(target)

        return False

    def bite(self, target):
        self.game.add_message("%s bites %s!" % (self.name, target.name))
        damage = random.randint(1, 4)
        target.hp -= damage
        if target.hp <= 0:
            target.on_death()

        return True

    def eat(self, target):
        self.game.add_message("%s eats %s !" % (self.name, target.name))
        self.level.remove_actor(target)
        self.target = None
        if self.hp + 5 <= self.max_hp:
            self.hp += 5
        else:
            self.hp = self.max_hp

        return True


class Spider(Actor):
    def __init__(self, game, x, y):
        super().__init__(game, 10, "S", "Spider", x, y, team=Team.QueenSpider)
        self.target = None
        self.display_priority = 8
        self.max_hp = 20

    def act(self):
        if self.stunned > 0:
            self.stunned -= 1
            return

        if self.dead:
            return

        if self.target is None or self.target.level is None:
            goblins = [actor for actor in self.level.actors if actor.team == Team.Goblin]
            if not goblins:
                spider = next(actor for actor in self.level.actors if actor.is_player)
                return movement.step_to_target(self, spider)
            closest_goblin = utils.get_closest_actor(self, goblins)
            if closest_goblin.dead:
                dist = utils.get_distance(self, closest_goblin)
                if dist <= 1:
                    return self.eat(closest_goblin)
                else:
                    return movement.step_to_target(self, closest_goblin)
            return movement.step_to_target(self, closest_goblin)
        else:
            dist = utils.get_distance(self, self.target)
            if dist <= 1:
                return self.eat(self.target)
            else:
                return movement.step_to_target(self, self.target)

    def bump(self, target):
        if target is self.target or target.team == Team.Goblin:
            if target.dead:
                return self.eat(target)
            else:
                return self.bite(target)

        return False

    def bite(self, target):
        self.game.add_message("%s bites %s!" % (self.name, target.name))
        damage = random.randint(2, 8)
        target.hp -= damage
        if target.hp <= 0:
            target.on_death()

        return True

    def eat(self, target):
        self.game.add_message("%s eats %s !" % (self.name, target.name))
        self.level.remove_actor(target)
        self.target = None
        if self.hp + 5 <= self.max_hp:
            self.hp += 5
        else:
            self.hp = self.max_hp

        return True


class SpiderQueen(Actor):
    egg_delay = 11
    jump_delay = 6
    web_delay = 20

    def __init__(self, game, x, y):
        super().__init__(game, 20, "@", "You", x, y, team=Team.QueenSpider)
        self.egg_cool_down = 0
        self.jump_cool_down = 0
        self.web_cooldown = 0
        self.is_player = True
        self.corpse_eaten = 0
        self.kills = 0
        self.eggs_laid = 0
        self.enemies_crushed = 0
        self.webs_fired = 0
        self.moved = False
        self.display_priority = 1
        self.max_hp = 40

    def act(self):
        if self.stunned > 0:
            self.stunned -= 1
            self.moved = True
            return

        if self.dead:
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

        if self.moved:
            if self.egg_cool_down > 0:
                self.egg_cool_down -= 1
            if self.jump_cool_down > 0:
                self.jump_cool_down -= 1
            if self.web_cooldown > 0:
                self.web_cooldown -= 1

    def bump(self, target):
        return self.bite(target)

    def bite(self, target):
        self.game.add_message("You bite %s" % target.name)
        damage = random.randint(1, 8)
        target.hp -= damage
        if target.hp <= 0:
            target.on_death()
            self.kills += 1

        return True

    def eat(self, target):
        self.game.add_message("You eat %s !" % target.name)
        if self.hp + 5 <= self.max_hp:
            self.hp += 5
        else:
            self.hp = self.max_hp
        self.level.remove_actor(target)
        self.corpse_eaten += 1

        return True

    def fire_web(self):
        if self.web_cooldown > 0:
            self.game.add_message("You need to wait %s more rounds to fire web." % self.web_cooldown)
            return False

        self.game.add_message("Press direction to fire web", show_now=True)
        offset = utils.get_directional_pos()
        if offset is None:
            self.game.add_message("Cancelled", show_now=True)
            return False
        self.webs_fired += 1
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
                    actors = [actor for actor in self.level.get_actors(gx, gy) if not actor.dead]
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
            actors = self.level.get_actors(web_x, web_y)
            if actors:
                goblin = next((actor for actor in actors if actor.team == Team.Goblin and not actor.dead), None)
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
                    actors = [actor for actor in self.level.get_actors(gx, gy) if not actor.dead]
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
        self.eggs_laid += 1

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
        target = self.get_edible_target(self.level.get_actors(tx, ty))
        if target is not None:
            return self.eat(target)
        self.game.add_message("No corpses there.", show_now=True)
        return False

    def get_edible_target(self, targets):
        corpse = next((target for target in targets if target.dead), None)
        if corpse:
            return corpse

    def on_death(self):
        self.blocking = False
        self.dead = True
        self.display_char = "%"
        self.game.add_message("You are DEAD!")

    def jump_to(self, x, y):
        if self.level.get_tile(x, y) == ".":
            collides = self.level.get_actors(x, y)
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
                        self.enemies_crushed += 1

            self.x = x
            self.y = y
        else:
            return False
