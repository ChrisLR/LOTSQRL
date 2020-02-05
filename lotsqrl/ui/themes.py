class Theme(object):
    """
    Object containing style information
    """
    def __init__(self, active_color=None, inactive_color=None, active_bg_color=None, inactive_bg_color=None):
        self.active_color = active_color
        self.inactive_color = inactive_color
        self.active_bg_color = active_bg_color
        self.inactive_bg_color = inactive_bg_color


default_theme = Theme(active_color="yellow")
