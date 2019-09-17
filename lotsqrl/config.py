import configparser
import logging
import os

game_root = os.getcwd()
graphics_folder = os.path.join(game_root, "graphics")
config_file_path = os.path.join(game_root, 'config.ini')


def parse_bool(value):
    if value:
        if value is True:
            return True
        elif value.lower() in ("true", "yes"):
            return True
    return False


class OptionField(object):
    def __init__(self, name, default, option_type):
        self.name = name
        self.default = default
        self.option_type = option_type


class ConfigurableOptions(object):
    fields = ()

    def __init__(self, **options):
        for field in self.fields:
            value = options.get(field.name, field.default)
            setattr(self, field.name, field.option_type(value))

    def export(self):
        return {
            field.name: getattr(self, field.name, field.default)
            for field in self.fields
        }


class MainOptions(ConfigurableOptions):
    fields = (
        OptionField('graphical_tiles', True, parse_bool),
        OptionField('map_width', 25, int),
        OptionField('map_height', 25, int),
    )


class ScreenInfo(ConfigurableOptions):
    fields = (
        OptionField('cellsize', "8x16", str),
        OptionField('screen_width', 100, int),
        OptionField('screen_height', 50, int),
    )

    config_fields = ('cellsize', 'screen_width', 'screen_height')

    def __init__(self, **options):
        self.cellsize = ""
        self.screen_width = 0
        self.screen_height = 0
        super().__init__(**options)
        self.title = "Lair of the Spider Queen RL"
        self.game_area_width = self.screen_width
        self.half_width = int(self.screen_width / 2)
        self.half_height = int(self.screen_height / 2)
        self.message_log_height = 11
        self.top_gui_height = 5
        self.game_area_height = self.screen_height - self.message_log_height - self.top_gui_height


def load_ini():
    parser = configparser.ConfigParser()
    try:
        parser.read(config_file_path)
        options = MainOptions(**parser['options'])
        screen_info = ScreenInfo(**parser['screen_info'])
    except (IOError, KeyError):
        logging.warning("Could not read config file, writing the default one")
        options = MainOptions()
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
