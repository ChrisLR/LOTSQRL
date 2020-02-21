from bearlibterminal import terminal

from lotsqrl.ui.labels import Label


class PowersScene(object):
    CHAR_SET = "abcdefghijklmnopqrstuvwxyz0123456789"

    def __init__(self, actor):
        self.actor = actor
        self.keys = (c for c in self.CHAR_SET)
        self.powers = {
            next(self.keys): power for power in actor.actions.get_powers()
        }
        self.ui_elements = [
            Label(text=f"{power.key}: {power.name}")
            for power in self.powers.values()
        ]
        for ui_element in self.ui_elements:
            ui_element.rel_y += 1
        self.must_stop = True
        self.selected_power = None


    def draw(self):
        terminal.clear()
        for ui_element in self.ui_elements:
            ui_element.draw()
        terminal.refresh()

    def update(self, terminal_input):
        if terminal_input == terminal.TK_ESCAPE:
            self.actor.game.evolution_scene_active = False
            self.must_stop = True
            return

        char_key = chr(terminal.state(terminal.TK_WCHAR))
        power = self.powers.get(char_key)
        if power is not None:
            self.selected_power = power
            self.must_stop = True

    def start(self):
        self.must_stop = False

        while not self.must_stop:
            terminal.layer(0)
            self.draw()
            terminal_input = terminal.read()
            if terminal_input == terminal.TK_CLOSE:
                self.must_stop = True
            else:
                self.update(terminal_input)
