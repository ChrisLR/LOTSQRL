from lotsqrl.components import Display


class Tile(object):
    display = Display(None, "", "", "", 10)


class CaveWall(Tile):
    display = Display(None, "#", "#daa520", "#", 10)


class CaveFloor(Tile):
    display = Display(None, ".", "gray", ".", 10)
