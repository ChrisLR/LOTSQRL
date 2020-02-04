class Theme(object):
    """
    Object containing style information
    """
    def __init__(self, active_color=None, inactive_color=None):
        self.active_color = active_color
        self.inactive_color = inactive_color


default_theme = Theme(active_color="yellow")
