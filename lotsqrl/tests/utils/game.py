import sys

from bearlibterminal import terminal

from lotsqrl import tiles
from lotsqrl.config import MainOptions, ScreenInfo
from lotsqrl.game import Game
from lotsqrl.level import Level
from lotsqrl.scenes import mainmenu


class TestGame(Game):
    def prepare(self):
        self.level = Level(self.options.map_width, self.options.map_height)
        self.level.path_grid = [[0 if c == tiles.CaveWall else 1 for c in row]
                                for row in self.level.tiles]
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

            terminal.clear()
            self.scene.draw_top_gui()
            self.camera.draw()
            self.scene.update_messages()
            terminal.refresh()


class GameController:
    def __init__(self, graphics_base_dir="../../../graphics", starting_actors=None):
        self.screen_info = ScreenInfo()
        self.graphics_base_dir = graphics_base_dir
        self.starting_actors = starting_actors if starting_actors is not None else []

    def prepare_terminal(self):
        running = terminal.open()
        if running:
            terminal.set(
                "window: size=%sx%s, title=%s, cellsize=%s" %
                (
                    self.screen_info.screen_width,
                    self.screen_info.screen_height,
                    self.screen_info.title,
                    self.screen_info.cellsize
                )
            )
        else:
            raise Exception("Terminal could not open.")

    def start(self):
        options = MainOptions(graphics_base_dir=self.graphics_base_dir)
        self.prepare_terminal()

        closing = False
        while not closing:
            closing = True
            game = TestGame(options, self.screen_info)
            mainmenu.main_screen_loop()
            game.prepare()
            for actor in self.starting_actors:
                actor.game = game
                adjust_actor_from_center(actor, game)
                game.level.add_actor(actor)
            game.run()
            if game.should_restart:
                closing = False
        terminal.close()


def adjust_actor_from_center(actor, game: TestGame):
    actor.x += game.player.x
    actor.y += game.player.y
