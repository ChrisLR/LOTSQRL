class Tile(object):
    char = ""
    color = ""

    @classmethod
    @property
    def as_string(cls):
        return "[color=red]%s[/color]" % cls.char


class CaveWall(Tile):
    char = "#"
    color = "brown"


class CaveFloor(Tile):
    char = "."
    color = "gray"
