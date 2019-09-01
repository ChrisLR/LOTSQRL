from bearlibterminal import terminal


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

        terminal.layer(1)
        draw_offset_y = screen_info.top_gui_height + 1
        for y, row_tiles in enumerate(level.tiles):
            dy = y - oy
            for x, tile in enumerate(row_tiles):
                dx = (x * 2) - ox
                if x * 2 > max_x or y > max_y or x * 2 < ox or y < oy:
                    continue
                terminal.put(dx, dy + draw_offset_y, tile)

        terminal.layer(3)
        for actor in sorted(level.actors, key=lambda a: a.display_priority, reverse=True):
            dx = (actor.x * 2) - ox
            dy = actor.y - oy

            if actor.x > max_x or actor.y > max_y or actor.x < ox or actor.y < oy:
                continue
            terminal.put(dx, dy + draw_offset_y, actor.display_char)
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

        terminal.set("tile 0x28: graphics\\cocoon.png, size=16x16, spacing=2x1;")
        terminal.set("tile 0x30: graphics\\egg.png, size=16x16, spacing=2x1;")
        terminal.set("tile 0x67: graphics\\goblin.png, size=16x16, spacing=2x1;")
        terminal.set("tile 0x47: graphics\\goblin-chief.png, size=16x16, spacing=2x1")
        terminal.set("tile 0x2e: graphics\\floor2.png, size=16x16, spacing=2x1;")
        terminal.set("tile 0x25: graphics\\skull.png, size=16x16, spacing=2x1;")
        terminal.set("tile 0x53: graphics\\spider.png, size=16x16, spacing=2x1;")
        terminal.set("tile 0x73: graphics\\spiderling.png, size=16x16, spacing=2x1;")
        terminal.set("tile 0x40: graphics\\spiderqueen.png, size=16x16, spacing=2x1;")
        terminal.set("tile 0x23: graphics\\wall2.png, size=16x16, spacing=2x1;")
        terminal.set("tile 0x2f: graphics\\webdiagonal2.png, size=16x16, spacing=2x1")
        terminal.set("tile 0x5c: graphics\\webdiagonal.png, size=16x16, spacing=2x1")
        terminal.set("tile 0x2d: graphics\\webhorizontal.png, size=16x16, spacing=2x1")
        terminal.set("tile 0x7c: graphics\\webvertical.png, size=16x16, spacing=2x1")

    def set_sprite_font(self):
        if not self.options.graphical_tiles:
            return
        terminal.font("tile")

    def reset_font(self):
        if not self.options.graphical_tiles:
            return
        terminal.font("")
