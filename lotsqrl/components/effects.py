from lotsqrl.components.base import Component


class Effects(Component):
    def __init__(self, host):
        super().__init__(host)
        self._effects = {}

    def get_by_name(self, name):
        return self._effects.get(name, 0)

    def set(self, name, effect):
        effect.on_start()
        self._effects[name] = effect

    def update(self):
        effects = list(self._effects.values())
        for effect in effects:
            if effect.lifetime == 0:
                effect.on_finish()
                del self._effects[effect.name]
            else:
                effect.update()

    def on_death(self):
        for effect in self._effects.values():
            effect.on_death()
