class Tile(object):
    char = ""
    color = ""

    @classmethod
    def ascii_str(cls):
        return "[color=%s]%s[/color]" % (cls.color, cls.char)


class CaveWall(Tile):
    char = "#"
    color = "#daa520"


class CaveFloor(Tile):
    char = "."
    color = "gray"
