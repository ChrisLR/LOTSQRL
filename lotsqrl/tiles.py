class Tile(object):
    display_char = ""
    color = ""

    @classmethod
    def ascii_str(cls):
        return "[color=%s]%s[/color]" % (cls.color, cls.display_char)


class CaveWall(Tile):
    display_char = "#"
    color = "#daa520"


class CaveFloor(Tile):
    display_char = "."
    color = "gray"
