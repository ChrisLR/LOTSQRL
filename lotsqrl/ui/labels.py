from bearlibterminal import terminal
from lotsqrl.ui.base import UIElement
from lotsqrl.ui import utils


class Label(UIElement):
    def __init__(self, parent=None, rel_x=0, rel_y=0, theme=None, text=None):
        super().__init__(parent, rel_x, rel_y, theme=theme)
        self.text = text

    def draw(self):
        if not self.text:
            return

        colorized_text = utils.colorize_text(self, self.text)
        terminal.printf(self.x, self.y, colorized_text)


class DynamicLabel(Label):
    def __init__(self, getter, parent=None, rel_x=0, rel_y=0, theme=None):
        super().__init__(parent, rel_x, rel_y, theme=theme)
        self.getter = getter

    def draw(self):
        self.text = str(self.getter())
        super().draw()
