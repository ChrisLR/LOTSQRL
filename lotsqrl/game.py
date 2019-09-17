import random
import sys

from bearlibterminal import terminal

from lotsqrl import actors, automata
from lotsqrl.camera import Camera
from lotsqrl.scenes.game import GameScene
from lotsqrl.teams import Team


class Game(object):
    def __init__(self, options, screen_info):
        self.boss = actors.GoblinChief(self, 0, 0)
        self.player = actors.SpiderQueen(self, 0, 0)
        self.camera = Camera(self.player, options, screen_info)
        self.game_won = False
        self.options = options
        self.screen_info = screen_info
        self.messages = []
        self.level = None
        self.running = False
        self.should_restart = False
        self.scene = GameScene(self, screen_info)
        self.turn = 0

    def add_message(self, message, show_now=False):
        self.messages.append(message)
        if show_now:
            self.scene.update_messages()
            terminal.refresh()

    def prepare(self):
        automata_steps = 4  # Usually gives a nice layout
        self.level = automata.generate_map(self.options.map_width, self.options.map_height, automata_steps)
        spawn_x, spawn_y = self.select_player_spawn()
        self.player.x = spawn_x
        self.player.y = spawn_y
        self.player.stunned = 1  # This skips turn 0
        self.level.add_actor(self.player)

    def run(self):
        self.running = True
        while self.running:
            boss = self.boss
            level = self.level
            player = self.player

            if not player.dead:
                player.act()
                if self.should_restart is True:
                    return
            else:
                if terminal.has_input():
                    key_press = terminal.read()
                    if key_press == terminal.TK_CLOSE:
                        sys.exit()
                    elif key_press == terminal.TK_ESCAPE:
                        self.should_restart = True
                        return

            if player.moved:
                player.moved = False
                if not boss.dead:
                    self.turn += 1
                for actor in level.actors.copy():
                    if actor is player:
                        continue
                    if actor.level is not None:
                        actor.act()

            turn = self.turn
            if turn >= 10 and turn % 10 == 0 and not boss.dead and not player.dead:
                self.spawn_goblins(turn)

            if boss.dead and not level.get_actors_by_team(Team.Goblin):
                self.game_won = True

            terminal.clear()
            self.scene.draw_top_gui()
            self.camera.draw()
            self.scene.update_messages()
            terminal.refresh()

    def spawn_goblins(self, turn):
        level = self.level
        spawn_points = level.spawns
        amount = random.randint(1, min(int(turn / 10), 12))
        for _ in range(amount):
            x, y = random.choice(spawn_points)
            level.add_actor(actors.Goblin(self, x, y))

        if turn == 500 and self.boss.level is None:
            x, y = random.choice(spawn_points)
            self.boss.x = x
            self.boss.y = y
            level.add_actor(self.boss)

    def select_player_spawn(self):
        level = self.level
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

        raise ValueError("No Suitable Player Spawn")
