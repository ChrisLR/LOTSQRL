from lotsqrl.ui.themes import default_theme


class UIElement(object):
    def __init__(self, parent=None, rel_x=0, rel_y=0, theme=None):
        self.parent = parent
        self.rel_x = rel_x
        self.rel_y = rel_y
        self.theme = theme or default_theme
        self.is_active = False

    def draw(self):
        pass

    def update(self, terminal_input):
        pass

    @property
    def x(self):
        if self.parent is not None:
            return self.parent.x + self.rel_x
        return self.rel_x

    @property
    def y(self):
        if self.parent is not None:
            return self.parent.y + self.rel_y
        return self.rel_y
