class Effect(object):
    name = ""

    def __init__(self, host, lifetime):
        self.host = host
        self.lifetime = lifetime

    def update(self):
        if self.lifetime > 0:
            self.lifetime -= 1

    def on_start(self):
        pass

    def on_finish(self):
        pass

    def on_cancel(self):
        pass

    def on_death(self):
        pass
