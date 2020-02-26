from lotsqrl.components.base import Component


class Display(Component):
    def __init__(self, host, ascii_char, ascii_color, tile_char, display_priority):
        super().__init__(host)
        self.ascii_char = ascii_char
        self.ascii_color = ascii_color
        self.tile_char = tile_char or ascii_char
        self.display_priority = display_priority

    def ascii_str(self):
        return "[color=%s]%s[/color]" % (self.ascii_color, self.ascii_char)
