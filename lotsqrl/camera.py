import os

from bearlibterminal import terminal

from lotsqrl import config


class Camera(object):
    def __init__(self, focus_on, options, screen_info):
        self.options = options
        self.screen_info = screen_info
        self.focus_on = focus_on
        self.load_sprites()

    def draw(self):
        screen_info = self.screen_info
        self.set_sprite_font()
        half_width, half_height = screen_info.half_width, screen_info.half_height - screen_info.message_log_height
        ox, oy = (self.focus_on.x * 2) - half_width, self.focus_on.y - half_height
        max_x, max_y = ox + screen_info.game_area_width, oy + screen_info.game_area_height
        level = self.focus_on.level
        graphics = self.options.graphical_tiles

        terminal.layer(1)
        draw_offset_y = screen_info.top_gui_height + 1
        for y, row_tiles in enumerate(level.tiles):
            dy = y - oy
            for x, tile in enumerate(row_tiles):
                dx = (x * 2) - ox
                if x * 2 > max_x or y > max_y or x * 2 < ox or y < oy:
                    continue

                # TODO Stop checking graphics for every draw
                if graphics is True:
                    terminal.put(dx, dy + draw_offset_y, tile.char)
                else:
                    terminal.printf(dx, dy + draw_offset_y, tile.ascii_str())

        terminal.layer(3)
        for actor in sorted(level.actors, key=lambda a: a.display_priority, reverse=True):
            dx = (actor.x * 2) - ox
            dy = actor.y - oy

            if actor.x > max_x or actor.y > max_y or actor.x < ox or actor.y < oy:
                continue

            # TODO Stop checking graphics for every draw
            if graphics is True:
                terminal.put(dx, dy + draw_offset_y, actor.display_char)
            else:
                terminal.printf(dx, dy + draw_offset_y, actor.ascii_str())

        self.reset_font()

    def transform(self, x, y):
        screen_info = self.screen_info
        draw_offset_y = screen_info.top_gui_height + 1
        half_width, half_height = screen_info.half_width, screen_info.half_height - screen_info.message_log_height
        ox, oy = (self.focus_on.x * 2) - half_width, self.focus_on.y - half_height

        return (x * 2) - ox, (y - oy) + draw_offset_y

    def load_sprites(self):
        if not self.options.graphical_tiles:
            return
        
        for char, sprite_name in sprite_chars:
            sprite_path = os.path.join(config.graphics_folder, sprite_name)
            terminal.set("{}: {}, size=16x16, spacing=2x1;".format(char, sprite_path))

    def set_sprite_font(self):
        if not self.options.graphical_tiles:
            return
        terminal.font("tile")

    def reset_font(self):
        if not self.options.graphical_tiles:
            return
        terminal.font("")


sprite_chars = (
    (f'tile 0x28', 'cocoon.png'),
    (f'tile 0x30', 'egg.png'),
    (f'tile 0x67', 'goblin.png'),
    (f'tile 0x47', 'goblin-chief.png'),
    (f'tile 0x2e', 'floor2.png'),
    (f'tile 0x25', 'skull.png'),
    (f'tile 0x53', 'spider.png'),
    (f'tile 0x73', 'spiderling.png'),
    (f'tile 0x40', 'spiderqueen.png'),
    (f'tile 0x23', 'wall2.png'),
    (f'tile 0x2f', 'webdiagonal2.png'),
    (f'tile 0x5c', 'webdiagonal.png'),
    (f'tile 0x2d', 'webhorizontal.png'),
    (f'tile 0x7c', 'webvertical.png'),
)
