from bearlibterminal import terminal

class InputMapping(object):
    _mapping = {}

    def get(self, key):
        return self._mapping.get(key)


class SystemMapping(InputMapping):
    _mapping = {
        terminal.TK_CLOSE: "exit_game",
        terminal.TK_F1: "open_manual",
        terminal.TK_ESCAPE: "new_game"
    }


class SpiderQueen(InputMapping):
    _mapping = {
        terminal.TK_E: "eat_corpse",
        terminal.TK_L: "lay_egg",
        terminal.TK_J: "jump",
        terminal.TK_KP_5: "wait",
        terminal.TK_F: "spin_cocoon",
    }
