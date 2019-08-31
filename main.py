import math
import random
import time
from enum import IntEnum

from bearlibterminal import terminal


class Team(IntEnum):
    QueenSpider = 0
    Goblin = 1


class Camera(object):
    def __init__(self, focus_on):
        self.focus_on = focus_on

    def draw(self):
        set_sprite_font()
        half_width, half_height = int(game_area_width / 2), int(game_area_height / 2)
        ox, oy = (self.focus_on.x * 2) - half_width, self.focus_on.y - half_height
        max_x, max_y = ox + game_area_width, oy + game_area_height
        level = self.focus_on.level

        terminal.layer(1)
        draw_offset_y = top_gui_height + 1
        for y, row_tiles in enumerate(level.tiles):
            dy = y - oy
            for x, tile in enumerate(row_tiles):
                dx = (x * 2) - ox
                if x * 2 > max_x or y > max_y or x * 2 < ox or y < oy:
                    continue
                terminal.put(dx, dy + draw_offset_y, tile)

        terminal.layer(3)
        for actor in sorted(level.actors, key=lambda actor: actor.display_priority, reverse=True):
            dx = (actor.x * 2) - ox
            dy = actor.y - oy

            if actor.x > max_x or actor.y > max_y or actor.x < ox or actor.y < oy:
                continue
            terminal.put(dx, dy + draw_offset_y, actor.display_char)
        reset_font()

    def transform(self, x, y):
        draw_offset_y = top_gui_height + 1
        half_width, half_height = int(game_area_width / 2), int(game_area_height / 2)
        ox, oy = (self.focus_on.x * 2) - half_width, self.focus_on.y - half_height
        return (x * 2) - ox, (y - oy) + draw_offset_y


class GameObject(object):
    def __init__(self, display_char="", name="", x=0, y=0, team=None):
        self.display_char = display_char
        self.name = name
        self.x = x
        self.y = y
        self.level = None
        self.blocking = True
        self.team = team
        self.is_player = False
        self.display_priority = 10


class Actor(GameObject):
    def __init__(self, hp, display_char="", name="", x=0, y=0, team=None):
        super().__init__(display_char, name, x, y, team=team)
        self.hp = hp
        self.max_hp = hp
        self.dead = False
        self.display_priority = 9
        self.stunned = 0

    def act(self):
        pass

    def bump(self, target):
        pass

    def on_death(self):
        self.blocking = False
        self.dead = True
        self.display_char = "%"
        self.display_priority = 10
        messages.append(self.name + " is dead!")


class Level(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.actors = []
        self.tiles = [["." for _ in range(width)] for _ in range(height)]
        self.spawns = []
        for i in range(width):
            self.tiles[0][i] = "#"
            self.tiles[height - 1][i] = "#"

        for i in range(height):
            self.tiles[i][0] = "#"
            self.tiles[i][width - 1] = "#"

    def add_actor(self, actor):
        self.actors.append(actor)
        actor.level = self

    def remove_actor(self, actor):
        self.actors.remove(actor)
        actor.level = None

    def get_tile(self, x, y):
        try:
            return self.tiles[y][x]
        except IndexError:
            return None

    def get_actors(self, x, y):
        return [actor for actor in self.actors if actor.x == x and actor.y == y]


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


class Egg(Actor):
    def __init__(self, x, y):
        super().__init__(1, "0", "Egg", x, y, team=Team.QueenSpider)
        self.hatch_countdown = 10
        self.display_priority = 9

    def act(self):
        if self.dead:
            return

        self.hatch_countdown -= 1
        if self.hatch_countdown <= 0:
            self.level.add_actor(Spiderling(self.x, self.y))
            self.level.remove_actor(self)


class Cocoon(Actor):
    def __init__(self, x, y):
        super().__init__(1, "(", "Cocoon", x, y, team=Team.QueenSpider)
        self.hatch_countdown = 10
        self.display_priority = 9
        self.burrowed = False

    def act(self):
        if self.dead:
            return

        if self.burrowed is True:
            self.hatch_countdown -= 1
            if self.hatch_countdown <= 0:
                self.level.add_actor(Spider(self.x, self.y))
                self.level.remove_actor(self)


class Spiderling(Actor):
    def __init__(self, x, y):
        super().__init__(4, "s", "Spiderling", x, y, team=Team.QueenSpider)
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
                return step_to_target(self, spider)
            target = get_closest_actor(self, targets)
            if target.dead:
                dist = get_distance(self, target)
                if dist <= 1:
                    return self.eat(target)
                else:
                    return step_to_target(self, target)
            return step_to_target(self, target)
        else:
            dist = get_distance(self, self.target)
            if dist <= 1:
                return self.eat(self.target)
            else:
                return step_to_target(self, self.target)

    def bump(self, target):
        if isinstance(target, Cocoon):
            messages.append("%s burrows into %s!" % (self.name, target.name))
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
        messages.append("%s bites %s!" % (self.name, target.name))
        damage = random.randint(1, 4)
        target.hp -= damage
        if target.hp <= 0:
            target.on_death()

        return True

    def eat(self, target):
        messages.append("%s eats %s !" % (self.name, target.name))
        self.level.remove_actor(target)
        self.target = None
        if self.hp + 5 <= self.max_hp:
            self.hp += 5
        else:
            self.hp = self.max_hp

        return True


class Spider(Actor):
    def __init__(self, x, y):
        super().__init__(10, "S", "Spider", x, y, team=Team.QueenSpider)
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
                return step_to_target(self, spider)
            closest_goblin = get_closest_actor(self, goblins)
            if closest_goblin.dead:
                dist = get_distance(self, closest_goblin)
                if dist <= 1:
                    return self.eat(closest_goblin)
                else:
                    return step_to_target(self, closest_goblin)
            return step_to_target(self, closest_goblin)
        else:
            dist = get_distance(self, self.target)
            if dist <= 1:
                return self.eat(self.target)
            else:
                return step_to_target(self, self.target)

    def bump(self, target):
        if target is self.target or target.team == Team.Goblin:
            if target.dead:
                return self.eat(target)
            else:
                return self.bite(target)

        return False

    def bite(self, target):
        messages.append("%s bites %s!" % (self.name, target.name))
        damage = random.randint(2, 8)
        target.hp -= damage
        if target.hp <= 0:
            target.on_death()

        return True

    def eat(self, target):
        messages.append("%s eats %s !" % (self.name, target.name))
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

    def __init__(self, x, y):
        super().__init__(20, "@", "You", x, y, team=Team.QueenSpider)
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
        move_action = move_actions.get(press)
        if move_action is not None:
            self.moved = move_action(player)

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
            exit()
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
        messages.append("You bite %s" % target.name)
        damage = random.randint(1, 8)
        target.hp -= damage
        if target.hp <= 0:
            target.on_death()
            self.kills += 1

        return True

    def eat(self, target):
        messages.append("You eat %s !" % target.name)
        if self.hp + 5 <= self.max_hp:
            self.hp += 5
        else:
            self.hp = self.max_hp
        self.level.remove_actor(target)
        self.corpse_eaten += 1

        return True

    def fire_web(self):
        if self.web_cooldown > 0:
            messages.append("You need to wait %s more rounds to fire web." % self.web_cooldown)
            return False

        messages.append("Press direction to fire web")
        update_messages()
        terminal.refresh()
        offset = get_directional_pos()
        if offset is None:
            messages.append("Cancelled")
            return False
        self.webs_fired += 1
        self.web_cooldown = 20

        for i in range(10):
            web_x, web_y = self.x + (offset[0] * i), self.y + (offset[1] * i)
            if self.level.get_tile(web_x, web_y) == "#":
                messages.append("Your web hits a wall, press a key to fling yourself.")
                update_messages()
                terminal.refresh()
                offset = get_directional_pos()
                if offset is None:
                    messages.append("You snap your web with your fangs")
                    return True
                for wf in range(1, 5):
                    gx, gy = self.x + (offset[0] * wf), self.y + (offset[1] * wf)
                    actors = [actor for actor in self.level.get_actors(gx, gy) if not actor.dead]
                    if actors:
                        actor = actors[0]
                        messages.append("You smash against %s!" % actor.name)
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

            web_char = direction_offsets_char.get(offset)
            terminal.layer(2)
            set_sprite_font()
            terminal.put(*camera.transform(web_x, web_y), web_char)
            reset_font()
            terminal.layer(3)
            terminal.refresh()
            time.sleep(0.05)
            actors = self.level.get_actors(web_x, web_y)
            if actors:
                goblin = next((actor for actor in actors if actor.team == Team.Goblin and not actor.dead), None)
                if goblin is None:
                    continue
                messages.append("You web latches on %s!" % goblin.name)
                messages.append("Press direction to fling %s" % goblin.name)
                update_messages()
                terminal.refresh()
                offset = get_directional_pos()
                if offset is None:
                    messages.append("You snap your web with your fangs")
                    return True
                messages.append("You fling %s in the air!" % goblin.name)
                for wf in range(1, 5):
                    gx, gy = goblin.x + (offset[0] * wf), goblin.y + (offset[1] * wf)
                    actors = [actor for actor in self.level.get_actors(gx, gy) if not actor.dead]
                    if actors:
                        actor = actors[0]
                        if actor == self and goblin != goblin_chief:
                            messages.append("You catch %s and start spinning a cocoon!" % goblin.name)
                            goblin.dead = True
                            self.level.remove_actor(goblin)
                            new_cocoon = Cocoon(gx - offset[0], gy - offset[1])
                            self.level.add_actor(new_cocoon)
                            return True
                        messages.append("%s smashes against %s!" % (goblin.name, actor.name))
                        goblin.stunned = 1
                        if actor != player:
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
                            messages.append("%s smashes against the wall!" % goblin.name)
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
            messages.append("There is no one to web there.")

        return False

    def lay_egg(self):
        if self.egg_cool_down > 0:
            messages.append("You need to wait %s more rounds to lay." % self.egg_cool_down)
            return False

        messages.append("You lay an egg.")
        new_egg = Egg(self.x, self.y)
        self.level.add_actor(new_egg)
        self.egg_cool_down = self.egg_delay
        self.eggs_laid += 1

        return True

    def jump(self):
        if self.jump_cool_down > 0:
            messages.append("You need to wait %s more rounds to jump." % self.jump_cool_down)
            return False

        messages.append("Press direction to jump")
        update_messages()
        terminal.refresh()
        offset = get_directional_pos()
        if offset is None:
            messages.append("Cancelled")
            return False

        ox, oy = offset
        if ox != 0:
            ox *= 3
        if oy != 0:
            oy *= 3

        jumped = self.jump_to(self.x + ox, self.y + oy)
        if jumped is False:
            messages.append("Can't jump there, a wall in the way.")
            return False
        else:
            self.jump_cool_down = self.jump_delay
            return True

    def try_eat(self):
        messages.append("Press direction to eat corpse")
        update_messages()
        terminal.refresh()
        offset = get_directional_pos()
        if offset is None:
            messages.append("Cancelled")
            return False

        tx, ty = self.x + offset[0], self.y + offset[1]
        target = self.get_edible_target(self.level.get_actors(tx, ty))
        if target is not None:
            return self.eat(target)
        return False

    def get_edible_target(self, targets):
        corpse = next((target for target in targets if target.dead), None)
        if corpse:
            return corpse

    def on_death(self):
        self.blocking = False
        self.dead = True
        self.display_char = "%"
        messages.append("You are DEAD!")

    def jump_to(self, x, y):
        if self.level.get_tile(x, y) == ".":
            collides = self.level.get_actors(x, y)
            collisions = [collide for collide in collides if collide is not self and collide.blocking]
            if collisions:
                messages.append("You leap into %s" % ','.join((collision.name for collision in collisions)))
                dx, dy = get_actor_delta(self, collisions[0])
                dx = sign(dx) * 2
                dy = sign(dy) * 2

                for collision in collisions:
                    collision.hp -= random.randint(1, 3)
                    moved = move_to(collision, collision.x + dx, collision.y + dy, bump=False)
                    if moved is False and collision is not goblin_chief:
                        messages.append("%s is crushed under you!" % collision.name)
                        collision.on_death()
                        self.enemies_crushed += 1

            self.x = x
            self.y = y
        else:
            return False


def move_north(actor):
    return move_to(actor, actor.x, actor.y - 1)


def move_northeast(actor):
    return move_to(actor, actor.x + 1, actor.y - 1)


def move_east(actor):
    return move_to(actor, actor.x + 1, actor.y)


def move_southeast(actor):
    return move_to(actor, actor.x + 1, actor.y + 1)


def move_south(actor):
    return move_to(actor, actor.x, actor.y + 1)


def move_southwest(actor):
    return move_to(actor, actor.x - 1, actor.y + 1)


def move_west(actor):
    return move_to(actor, actor.x - 1, actor.y)


def move_northwest(actor):
    return move_to(actor, actor.x - 1, actor.y - 1)


def move_to(actor, x, y, bump=True):
    level = actor.level
    if not level:
        return

    if level.get_tile(x, y) == ".":
        collides = actor.level.get_actors(x, y)
        collision = next((collide for collide in collides if collide is not actor and collide.blocking), None)
        if collision is not None and bump is True:
            return actor.bump(collision)
        else:
            actor.x = x
            actor.y = y
            return True
    else:
        return False


def get_closest_actor(origin, actors):
    return min(actors, key=lambda actor: get_distance(origin, actor))


def step_to_target(actor, target):
    target_dx, target_dy = get_actor_delta(actor, target)
    sx = sign(target_dx)
    sy = sign(target_dy)
    tx = actor.x + sx
    ty = actor.y + sy

    result = move_to(actor, tx, ty)
    if result:
        return result

    fx, fy = avoid_obstacle(actor, target, sx, sy)

    return move_to(actor, actor.x + fx, actor.y + fy)


def get_actor_delta(actor, target):
    return target.x - actor.x, target.y - actor.y


def sign(number):
    if number > 0:
        return 1
    elif number == 0:
        return 0
    elif number < 0:
        return -1


def get_distance(actor, target):
    return abs(target.x - actor.x) + abs(target.y - actor.y)


def bump(actor, target):
    if random.randint(0, 100) > 79:
        messages.append("%s kills %s" % (actor.name, target.name))
        target.on_death()
    else:
        messages.append("YOU MISS")


move_actions = {
    terminal.TK_KP_8: move_north,
    terminal.TK_KP_9: move_northeast,
    terminal.TK_KP_6: move_east,
    terminal.TK_KP_3: move_southeast,
    terminal.TK_KP_2: move_south,
    terminal.TK_KP_1: move_southwest,
    terminal.TK_KP_4: move_west,
    terminal.TK_KP_7: move_northwest
}
direction_offsets = {
    terminal.TK_KP_8: (0, -1),
    terminal.TK_KP_9: (1, -1),
    terminal.TK_KP_6: (1, 0),
    terminal.TK_KP_3: (1, 1),
    terminal.TK_KP_2: (0, 1),
    terminal.TK_KP_1: (-1, 1),
    terminal.TK_KP_4: (-1, 0),
    terminal.TK_KP_7: (-1, -1)
}

direction_offsets_char = {
    (0, -1): "|",
    (1, -1): "/",
    (1, 0): "-",
    (1, 1): "\\",
    (0, 1): "|",
    (-1, 1): "/",
    (-1, 0): "-",
    (-1, -1): "\\"
}


def game_loop(level):
    game_turn = 0
    while running:
        if not player.dead:
            player.act()
        else:
            if terminal.has_input():
                if terminal.read() == terminal.TK_CLOSE:
                    exit()
            time.sleep(0.5)

        if player.moved or player.dead:
            for actor in level.actors.copy():
                if actor is player:
                    continue
                actor.act()

        if game_turn >= 10 and game_turn % 10 == 0 and not goblin_chief.dead and not player.dead:
            spawn_goblins(level, game_turn)

        if player.moved:
            player.moved = False
            if not goblin_chief.dead:
                game_turn += 1

        terminal.clear()
        draw_top_gui(player, game_turn)
        camera.draw()
        update_messages()
        terminal.refresh()


def spawn_goblins(level, turn):
    spawn_points = level.spawns
    amount = random.randint(1, min(int(math.ceil(turn / 10)), 12))
    for _ in range(amount):
        x, y = random.choice(spawn_points)
        level.add_actor(Goblin(x, y))

    if turn == 500 and goblin_chief.level is None:
        x, y = random.choice(spawn_points)
        goblin_chief.x = x
        goblin_chief.y = y
        level.add_actor(goblin_chief)


def update_messages():
    top_border = top_gui_height + game_area_height + 2
    bottom_border = screen_height - top_border
    terminal.clear_area(0, top_border, screen_width, bottom_border)
    terminal.printf(0, top_border, "-" * screen_width)
    terminal.printf(0, screen_height - 1, "-" * screen_width)
    y_offset = top_gui_height + game_area_height + 3
    for i, message in enumerate(messages[-message_log_height::]):
        terminal.printf(1, y_offset + i, message)


def get_directional_pos():
    handled = None
    while not handled:
        press = terminal.read()
        direction_offset = direction_offsets.get(press)
        if direction_offset is not None:
            return direction_offset

        if press == terminal.TK_ESCAPE:
            return


def avoid_obstacle(actor, target, offset_x, offset_y):
    if abs(target.x - actor.x) > abs(target.y - actor.y):
        if offset_y == 0:
            return offset_x, random.choice([-1, 1])
        else:
            return offset_x, offset_y * -1
    if offset_x == 0:
        return random.choice([-1, 1]), offset_y
    return offset_x * -1, offset_y


def draw_top_gui(player, turn):
    terminal.printf(0, 0, "-" * screen_width)
    terminal.printf(0, top_gui_height, "-" * screen_width)
    for i in range(1, top_gui_height):
        terminal.printf(0, i, "|")
        terminal.printf(screen_width - 1, i, "|")
    terminal.printf(2, 1, "Hp:%s" % player.hp)
    terminal.printf(2, 2, "Turn:%s" % turn)
    terminal.printf(11, 1, "Cooldowns")
    terminal.printf(11, 2, "Egg:%s" % player.egg_cool_down)
    terminal.printf(11, 3, "Jump:%s" % player.jump_cool_down)
    terminal.printf(11, 4, "Web:%s" % player.web_cooldown)

    terminal.printf(30, 1, "Kills:%s" % player.kills)
    terminal.printf(30, 2, "Eggs Laid:%s" % player.eggs_laid)
    terminal.printf(30, 3, "Crushed:%s" % player.enemies_crushed)
    terminal.printf(30, 4, "Webs Fired:%s" % player.webs_fired)

    if player.dead:
        terminal.printf(45, 4, "[color=red]You are dead![/color]")

    if goblin_chief.dead:
        terminal.printf(45, 4, "[color=green]You won![/color]")


def set_sprites():
    if not graphical_tiles:
        return

    terminal.set("tile 0x28: graphics\\cocoon.png, size=16x16, spacing=2x1;")
    terminal.set("tile 0x30: graphics\\egg.png, size=16x16, spacing=2x1;")
    terminal.set("tile 0x67: graphics\\goblin.png, size=16x16, spacing=2x1;")
    terminal.set("tile 0x47: graphics\\goblin-chief.png, size=16x16, spacing=2x1")
    terminal.set("tile 0x2e: graphics\\floor2.png, size=16x16, spacing=2x1;")
    terminal.set("tile 0x25: graphics\\skull.png, size=16x16, spacing=2x1;")
    terminal.set("tile 0x53: graphics\\spider.png, size=16x16, spacing=2x1;")
    terminal.set("tile 0x73: graphics\\spiderling.png, size=16x16, spacing=2x1;")
    terminal.set("tile 0x40: graphics\\spiderqueen.png, size=16x16, spacing=2x1;")
    terminal.set("tile 0x23: graphics\\wall2.png, size=16x16, spacing=2x1;")
    terminal.set("tile 0x2f: graphics\\webdiagonal2.png, size=16x16, spacing=2x1")
    terminal.set("tile 0x5c: graphics\\webdiagonal.png, size=16x16, spacing=2x1")
    terminal.set("tile 0x2d: graphics\\webhorizontal.png, size=16x16, spacing=2x1")
    terminal.set("tile 0x7c: graphics\\webvertical.png, size=16x16, spacing=2x1")


def set_sprite_font():
    if not graphical_tiles:
        return
    terminal.font("tile")


def seek_spawn_points(map_cells):
    possible_coordinates = []
    top_row = map_cells[0]
    for x, tile in enumerate(top_row):
        if tile == ".":
            possible_coordinates.append((x, 0))

    bottom_row = map_cells[-1]
    for x, tile in enumerate(bottom_row):
        if tile == ".":
            possible_coordinates.append((x, len(bottom_row) - 1))

    for y, row in enumerate(map_cells):
        left_tile = row[0]
        if left_tile == ".":
            possible_coordinates.append((0, y))

        right_tile = row[-1]
        if right_tile == ".":
            possible_coordinates.append((len(row) - 1, y))

    return possible_coordinates


def reset_font():
    if not graphical_tiles:
        return
    terminal.font("")


def count_alive_neighbours(map, x, y):
    count = 0
    for i in range(-1, 2):
        for j in range(-1, 2):
            neighbour_x = x + i
            neighbour_y = y + j
            if i == 0 and j == 0:
                pass
            elif neighbour_x < 0 or neighbour_y < 0 or neighbour_x >= len(map) or neighbour_y >= len(map[0]):
                count = count + 1
            elif map[neighbour_x][neighbour_y] == "#":
                count = count + 1

    return count


def do_simulation_step(old_map, width, height, birth_limit, death_limit):
    new_map = [["." for _ in range(width)] for _ in range(height)]
    for x in range(len(old_map)):
        for y in range(len(old_map[x])):
            nbs = count_alive_neighbours(old_map, x, y)
            if old_map[x][y] == "#":
                if nbs < death_limit:
                    new_map[x][y] = "."
                else:
                    new_map[x][y] = "#"
            else:
                if nbs > birth_limit:
                    new_map[x][y] = "#"
                else:
                    new_map[x][y] = "."

    return new_map


def rando_alive(chance):
    if random.randint(0, 100) <= chance:
        return "#"
    return "."


def generate_map(width, height, number_of_steps):
    tries = 10
    new_level = Level(width, height)
    while tries:
        map_cells = generate_map_cells(width, height, number_of_steps)
        spawns = seek_spawn_points(map_cells)
        if len(spawns) >= 6:
            new_level.tiles = map_cells
            new_level.spawns = spawns
            return new_level
        tries -= 1

    raise ValueError("Map could not generate with enough spawn points QQ")


def generate_map_cells(width, height, number_of_steps):
    map_cells = [[rando_alive(30) for _ in range(width)] for _ in range(height)]
    for _ in range(number_of_steps):
        map_cells = do_simulation_step(map_cells, width, height, 4, 3)

    return map_cells


def select_player_spawn(level):
    middle_x, middle_y = int(level.width / 2), int(level.height / 2)
    if level.get_tile(middle_x, middle_y) == ".":
        return middle_x, middle_y
    tries = 20
    while tries:
        middle_x += random.randint(-10, 10)
        middle_y += random.randint(-10, 10)
        if level.get_tile(middle_x, middle_y) == ".":
            return middle_x, middle_y
        tries -= 1

    raise ValueError("Could not find player spawn QQ")


def main_screen_loop():
    terminal.clear()
    terminal.printf(20, 11, "  / _ \\")
    terminal.printf(20, 12, "\_\(_)/_/")
    terminal.printf(20, 13, " _//o\\\\_")
    terminal.printf(20, 14, "  /   \\")

    terminal.printf(30, 8, "Lair of the Spider Queen")
    terminal.printf(30, 16, "Goblins are infiltrating your lair.")
    terminal.printf(30, 17, "Punish them, feast on their corpses.")
    terminal.printf(30, 18, "Grow your army from their remains.")
    terminal.printf(30, 25, "Press any key to Start")
    terminal.refresh()
    e = terminal.read()
    if e == terminal.TK_CLOSE:
        exit()
    terminal.clear()
    player.stunned = 1

    return


def draw_help_file():
    terminal.clear()
    lines = []
    try:
        with open("manual.txt", "r") as manual_file:
            lines = manual_file.readlines()

        for i, line in enumerate(lines):
            terminal.printf(1, i, line)
        terminal.refresh()
    except Exception:
        terminal.printf(1, 5, "Could not load manual file! Press any key to continue playing")
        terminal.refresh()
    terminal.read()


if __name__ == '__main__':
    graphical_tiles = True
    top_gui_height = 5
    game_area_width = 100
    game_area_height = 30
    message_log_height = 11
    screen_width = 100
    screen_height = 50
    game_won = False

    first_level = generate_map(25, 25, 4)
    player_spawn = select_player_spawn(first_level)
    player = SpiderQueen(*player_spawn)
    goblin_chief = GoblinChief(0, 0)

    first_level.add_actor(player)
    camera = Camera(player)
    messages = []
    running = terminal.open()
    terminal.set("window: size=%sx%s, title=Lair of the Spider Queen RL, cellsize=8x16" % (screen_width, screen_height))
    main_screen_loop()
    set_sprites()
    getting_dir = False
    game_loop(first_level)
    terminal.close()
