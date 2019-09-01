from bearlibterminal import terminal

from main import set_sprite_font, game_area_width, game_area_height, top_gui_height, reset_font


class Camera(object):
    def __init__(self, focus_on):
        self.focus_on = focus_on

    def draw(self):
        set_sprite_font()
        half_width, half_height = int(game_area_width / 2), int(game_area_height / 2)
        ox, oy = (self.focus_on.x * 2) - half_width, self.focus_on.y - half_height
        max_x, max_y = ox + game_area_width, oy + game_area_height
        level = self.focus_on.level

        terminal.layer(1)
        draw_offset_y = top_gui_height + 1
        for y, row_tiles in enumerate(level.tiles):
            dy = y - oy
            for x, tile in enumerate(row_tiles):
                dx = (x * 2) - ox
                if x * 2 > max_x or y > max_y or x * 2 < ox or y < oy:
                    continue
                terminal.put(dx, dy + draw_offset_y, tile)

        terminal.layer(3)
        for actor in sorted(level.actors, key=lambda actor: actor.display_priority, reverse=True):
            dx = (actor.x * 2) - ox
            dy = actor.y - oy

            if actor.x > max_x or actor.y > max_y or actor.x < ox or actor.y < oy:
                continue
            terminal.put(dx, dy + draw_offset_y, actor.display_char)
        reset_font()

    def transform(self, x, y):
        draw_offset_y = top_gui_height + 1
        half_width, half_height = int(game_area_width / 2), int(game_area_height / 2)
        ox, oy = (self.focus_on.x * 2) - half_width, self.focus_on.y - half_height
        return (x * 2) - ox, (y - oy) + draw_offset_y