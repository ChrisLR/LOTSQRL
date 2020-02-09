from lotsqrl.components.base import Component


class Cooldowns(Component):
    def __init__(self, host):
        super().__init__(host)
        self._cooldowns = {}

    def get(self, name):
        return self._cooldowns.get(name, 0)

    def set(self, name, value):
        self._cooldowns[name] = value

    def update(self):
        for key in self._cooldowns.keys():
            value = self._cooldowns[key]
            if value > 0:
                self._cooldowns[key] -= 1
