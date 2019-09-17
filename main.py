from bearlibterminal import terminal


from lotsqrl.game import Game
from lotsqrl import config
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
    options, screen_info = config.load_ini()
    prepare_terminal()

    closing = False
    while not closing:
        closing = True
        game = Game(options, screen_info)
        mainmenu.main_screen_loop()
        game.prepare()
        game.run()
        if game.should_restart:
            closing = False
    terminal.close()
