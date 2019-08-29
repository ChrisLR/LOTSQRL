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
        draw_offset_y = top_gui_height
        for y, row_tiles in enumerate(level.tiles):
            dy = y - oy
            for x, tile in enumerate(row_tiles):
                dx = (x * 2) - ox
                if x > max_x or y > max_y or x < ox or y < oy:
                    continue
                terminal.put(dx, dy + draw_offset_y, tile)

        terminal.layer(2)
        for actor in sorted(level.actors, key=lambda actor: actor.display_priority, reverse=True):
            dx = (actor.x * 2) - ox
            dy = actor.y - oy

            if actor.x > max_x or actor.y > max_y or actor.x < ox or actor.y < oy:
                continue
            terminal.put(dx, dy + draw_offset_y, actor.display_char)
        reset_font()


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
        if not self.dead:
            spiders = [actor for actor in self.level.actors
                       if actor.team == Team.QueenSpider and not actor.dead]
            if spiders:
                closest_spider = get_closest_actor(self, spiders)
                return step_to_target(self, closest_spider)

    def bump(self, target):
        return self.stab(target)

    def stab(self, target):
        messages.append(self.name + " stabs %s!" % target.name)
        damage = random.randint(1, 4)
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
        self.hatch_countdown = 20
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
        if self.dead:
            return

        if self.target is None or self.target.level is None:
            targets = [actor for actor in self.level.actors if actor.team == Team.Goblin or isinstance(actor, Cocoon)]
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

        return True


class Spider(Actor):
    def __init__(self, x, y):
        super().__init__(10, "S", "Spider", x, y, team=Team.QueenSpider)
        self.target = None
        self.display_priority = 8
        self.max_hp = 20

    def act(self):
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
        self.moved = False
        self.display_priority = 1
        self.max_hp = 40

    def act(self):
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

        for i in range(10):
            web_x, web_y = self.x + (offset[0] * i), self.y + (offset[1] * i)
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
                for wf in range(1, 5):
                    gx, gy = goblin.x + (offset[0] * wf), goblin.y + (offset[1] * wf)
                    actors = [actor for actor in self.level.get_actors(gx, gy) if not actor.dead]
                    if actors:
                        actor = actors[0]
                        if actor == self:
                            messages.append("You catch %s and start spinning a cocoon!" % goblin.name)
                            self.level.remove_actor(goblin)
                            new_cocoon = Cocoon(gx - offset[0], gy - offset[1])
                            self.level.add_actor(new_cocoon)

                            return True
                        messages.append("%s smashes against %s!" % (goblin.name, actor.name))
                        goblin.x = gx
                        goblin.y = gy
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
                            goblin.hp -= random.randint(4, 8)
                            if goblin.hp < 0:
                                goblin.on_death()
                            goblin.x = gx - offset[0]
                            goblin.y = gy - offset[1]
                            break
                else:
                    goblin.x = gx
                    goblin.y = gy


                self.web_cooldown = 20
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
                    if moved is False:
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
    if actor.level.get_tile(x, y) == ".":
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
    tx = actor.x + sign(target_dx)
    ty = actor.y + sign(target_dy)

    return move_to(actor, tx, ty)


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


def game_loop(level):
    game_turn = 1
    while running:
        if game_turn % 10 == 0:
            spawn_goblins(level, game_turn)

        if not player.dead:
            player.act()
        else:
            time.sleep(0.5)

        if player.moved or player.dead:
            game_turn += 1
            player.moved = False

            for actor in level.actors.copy():
                if actor is player:
                    continue
                actor.act()

        terminal.clear()
        draw_top_gui(player, game_turn)
        camera.draw()
        update_messages()
        terminal.refresh()


def spawn_goblins(level, turn):
    amount = random.randint(1, min(int(math.ceil(turn / 10)), level.width - 2))
    for _ in range(amount):
        x = random.randint(1, level.width - 1)
        y = level.height - 1
        level.add_actor(Goblin(x, y))


def update_messages():
    terminal.printf(0, top_gui_height + game_area_height + 2, "-" * screen_width)
    terminal.printf(0, screen_height - 1, "-" * screen_width)
    y_offset = top_gui_height + game_area_height + 3
    for i, message in enumerate(messages[-message_log_height::]):
        terminal.printf(0, y_offset + i, message)


def get_directional_pos():
    handled = None
    while not handled:
        press = terminal.read()
        direction_offset = direction_offsets.get(press)
        if direction_offset is not None:
            return direction_offset

        if press == terminal.TK_ESCAPE:
            return


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

    terminal.printf(30, 1, "Kills:%s" % player.kills)
    terminal.printf(30, 2, "Eggs Laid:%s" % player.eggs_laid)
    terminal.printf(30, 3, "Crushed:%s" % player.enemies_crushed)

    if player.dead:
        terminal.printf(45, 4, "[color=red]You are dead![/color]")


def set_sprites():
    if not graphical_tiles:
        return
    terminal.set("tile 0x67: graphics\\goblin.png, size=16x16, spacing=2x1;")
    terminal.set("tile 0x40: graphics\\spiderqueen.png, size=16x16, spacing=2x1;")
    terminal.set("tile 0x2e: graphics\\floor2.png, size=16x16, spacing=2x1;")
    terminal.set("tile 0x23: graphics\\wall2.png, size=16x16, spacing=2x1;")
    terminal.set("tile 0x73: graphics\\spiderling.png, size=16x16, spacing=2x1;")
    terminal.set("tile 0x30: graphics\\egg.png, size=16x16, spacing=2x1;")
    terminal.set("tile 0x25: graphics\\skull.png, size=16x16, spacing=2x1;")
    terminal.set("tile 0x28: graphics\\cocoon.png, size=16x16, spacing=2x1;")
    terminal.set("tile 0x53: graphics\\spider.png, size=16x16, spacing=2x1;")


def set_sprite_font():
    if not graphical_tiles:
        return
    terminal.font("tile")


def reset_font():
    if not graphical_tiles:
        return
    terminal.font("")


if __name__ == '__main__':
    graphical_tiles = True
    top_gui_height = 5
    right_gui_width = 20
    game_area_width = 80
    game_area_height = 30
    message_log_height = 11
    screen_width = 100
    screen_height = 50
    player = SpiderQueen(1, 1)
    first_level = Level(20, 20)
    first_level.add_actor(player)
    first_level.add_actor(Goblin(10, 10))
    first_level.add_actor(Goblin(15, 15))
    camera = Camera(player)
    messages = []
    running = terminal.open()
    terminal.set("window: size=%sx%s, title=Lair of the Spider Queen RL, cellsize=8x16" % (screen_width, screen_height))
    set_sprites()
    getting_dir = False
    game_loop(first_level)
    terminal.close()
