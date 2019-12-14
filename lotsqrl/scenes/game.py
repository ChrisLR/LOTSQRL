from bearlibterminal import terminal


class GameScene(object):
    def __init__(self, game, screen_info):
        self.game = game
        self.screen_info = screen_info

    def update_messages(self):
        screen_info = self.screen_info
        game_area_height = screen_info.game_area_height
        screen_width = screen_info.screen_width
        screen_height = screen_info.screen_height
        top_gui_height = screen_info.top_gui_height

        top_border = top_gui_height + game_area_height + 2
        bottom_border = screen_height - top_border

        terminal.clear_area(0, top_border, screen_width, bottom_border)
        terminal.printf(0, top_border, "-" * screen_width)
        terminal.printf(0, screen_height - 1, "-" * screen_width)
        y_offset = top_gui_height + game_area_height + 3

        messages = self.game.messages
        message_log_height = screen_info.message_log_height - 4
        for i, message in enumerate(messages[-message_log_height::]):
            terminal.printf(1, y_offset + i, message)

    def draw_top_gui(self):
        game = self.game
        screen_info = self.screen_info
        screen_width = screen_info.screen_width
        top_gui_height = screen_info.top_gui_height
        player = game.player
        turn = game.turn

        terminal.printf(0, 0, "-" * screen_width)
        terminal.printf(0, top_gui_height, "-" * screen_width)
        for i in range(1, top_gui_height):
            terminal.printf(0, i, "|")
            terminal.printf(screen_width - 1, i, "|")

        terminal.printf(2, 1, "Hp:%s" % player.hp)
        terminal.printf(2, 2, "Turn:%s" % turn)
        terminal.printf(11, 1, "Cooldowns")
        terminal.printf(11, 2, "Egg:%s" % player.cooldowns.get("lay_egg"))
        terminal.printf(11, 3, "Jump:%s" % player.cooldowns.get("jump"))
        terminal.printf(11, 4, "Web:%s" % player.cooldowns.get("spin_cocoon"))

        terminal.printf(30, 1, "Kills:%s" % player.score.kills)
        terminal.printf(30, 2, "Eggs Laid:%s" % player.score.eggs_laid)
        terminal.printf(30, 3, "Crushed:%s" % player.score.enemies_crushed)
        terminal.printf(30, 4, "Webs Fired:%s" % player.score.webs_fired)

        if player.dead:
            terminal.printf(45, 3, "[color=red]You are dead![/color]")
            terminal.printf(45, 4, "Press ESCAPE to go back to main menu")

        if self.game.game_won is True:
            terminal.printf(45, 3, "[color=green]You won![/color]")
            terminal.printf(45, 4, "Press ESCAPE to go back to main menu")
