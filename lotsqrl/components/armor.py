from lotsqrl.components.base import Component


class Armor(Component):
    def __init__(self, host, armor=None):
        super().__init__(host)
        self._armor = None
        self.set(armor)
        # TODO This must support using and removing multiple armor sets

    def reduce(self, damage):
        if self._armor is not None:
            return self._armor.reduce(damage)
        return damage

    def on_damaged(self, damage, attacker):
        if self._armor:
            self._armor.on_damaged(damage, attacker)

    def set(self, new_armor):
        if new_armor is None:
            self._armor = None
        else:
            self._armor = new_armor(self.host)
