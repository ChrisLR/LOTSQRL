class Cooldowns(object):
    def __init__(self, host):
        self.host = host
        self._cooldowns = {}

    def get(self, name):
        return self._cooldowns.get(name, 0)

    def update(self):
        for key in self._cooldowns.keys():
            value = self._cooldowns[key]
            if value > 0:
                self._cooldowns[key] -= 1
