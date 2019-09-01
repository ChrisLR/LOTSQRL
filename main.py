import math
import random
import time
import sys

from bearlibterminal import terminal
from lotsqrl import actors
from lotsqrl.camera import Camera
from lotsqrl.level import Level



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
                    sys.exit()
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
        level.add_actor(actors.Goblin(x, y))

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


def reset_font():
    if not graphical_tiles:
        return
    terminal.font("")


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
        sys.exit()
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
    player = actors.SpiderQueen(*player_spawn)
    goblin_chief = actors.GoblinChief(0, 0)

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
