import configparser
import logging
import os

game_root = os.getcwd()
graphics_folder = os.path.join(game_root, "graphics")
config_file_path = os.path.join(game_root, 'config.ini')


class OptionField(object):
    def __init__(self, name, default, option_type):
        self.name = name
        self.default = default
        self.option_type = option_type


class Options(object):
    fields = (
        OptionField('automata_steps', 4, int),
        OptionField('graphical_tiles', True, bool),
        OptionField('map_width', 25, int),
        OptionField('map_height', 25, int),
    )

    def __init__(self, **options):
        for field in self.fields:
            value = options.get(field.name, field.default)
            setattr(self, field.name, field.option_type(value))

    def export(self):
        return {name: getattr(self, name) for name in self.config_fields}


class ScreenInfo(object):
    config_fields = ('cellsize', 'screen_width', 'screen_height')

    def __init__(self, **options):
        self.cellsize = options.get('cellsize', "8x16")
        self.title = "Lair of the Spider Queen RL"
        self.screen_width = options.get('screen_width', 100)
        self.screen_height = options.get('screen_height', 50)
        self.message_log_height = 11
        self.top_gui_height = 5
        self.game_area_width = self.screen_width
        self.game_area_height = self.screen_height - self.message_log_height - self.top_gui_height
        self.half_width = int(self.screen_width / 2)
        self.half_height = int(self.screen_height / 2)

    def export(self):
        return {name: getattr(self, name) for name in self.config_fields}


def load_ini():
    parser = configparser.ConfigParser()
    try:
        parser.read(config_file_path)
        options = Options(**parser['options'])
        screen_info = ScreenInfo(**parser['screen_info'])
    except (IOError, KeyError):
        logging.warning("Could not read config file, writing the default one")
        options = Options()
        screen_info = ScreenInfo()
        save_ini(options, screen_info)

    return options, screen_info


def save_ini(options, screen_info):
    parser = configparser.ConfigParser()
    try:
        new_opts = {
            'options': options.export(),
            'screen_info': screen_info.export()
        }
        parser.update(new_opts)
        with open(config_file_path, 'w') as file_:
            parser.write(file_)
    except IOError:
        logging.error("Could not write config file.")
