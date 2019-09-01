from bearlibterminal import terminal

from lotsqrl.game import Game, Options, ScreenInfo
from lotsqrl.scenes import mainmenu


def prepare_terminal():
    running = terminal.open()
    if running:
        terminal.set(
            "window: size=%sx%s, title=%s, cellsize=%s" %
            (
                screen_info.screen_width,
                screen_info.screen_height,
                screen_info.title,
                screen_info.cellsize
            )
        )
    else:
        raise Exception("Terminal could not open.")


if __name__ == '__main__':
    options = Options()
    screen_info = ScreenInfo()
    prepare_terminal()
    game = Game(options, screen_info)
    mainmenu.main_screen_loop()
    game.prepare()
    game.run()
    terminal.close()
