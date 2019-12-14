from bearlibterminal import terminal

from lotsqrl import gameobjects, utils
from lotsqrl.selectors.base import Selector


class TouchDirectional(Selector):
    def get(self, actor):
        super().get(actor)
        offset = utils.get_directional_pos()
        if offset is None:
            actor.game.add_message("Cancelled", show_now=True)
            return terminal.TK_INPUT_CANCELLED

        ox, oy = offset
        targets = actor.level.get_actors_by_pos(actor.x + ox, actor.y + oy)
        filtered_targets = self._filter(actor, targets)

        return filtered_targets


class LineDirectional(Selector):
    def __init__(self, reach, message=None, filters=None):
        super().__init__(message, filters)
        self.reach = reach

    def get(self, actor):
        super().get(actor)
        offset = utils.get_directional_pos()
        if offset is None:
            actor.game.add_message("Cancelled", show_now=True)
            return terminal.TK_INPUT_CANCELLED

        ox, oy = offset
        max_x = actor.x + ox * self.reach
        max_y = actor.y + oy * self.reach
        target_line = utils.get_target_line(actor, gameobjects.GridTarget(max_x, max_y))
        targets = utils.get_obstacles_in_target_line(target_line)
        filtered_targets = self._filter(actor, targets)

        return filtered_targets


class GridPointDirectional(Selector):
    """
    A Selector taking in a direction and a reach to return a single grid point as a target
    """
    def __init__(self, reach, message=None, filters=None):
        super().__init__(message, filters)
        self.reach = reach

    def get(self, actor):
        super().get(actor)
        offset = utils.get_directional_pos()
        if offset is None:
            actor.game.add_message("Cancelled", show_now=True)
            return terminal.TK_INPUT_CANCELLED

        ox, oy = offset
        max_x = actor.x + ox * self.reach
        max_y = actor.y + oy * self.reach

        return gameobjects.GridTarget(max_x, max_y),
