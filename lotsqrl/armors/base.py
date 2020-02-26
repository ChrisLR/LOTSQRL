class Armor(object):
    def __init__(self, host):
        self.host = host

    def reduce(self, damage):
        return damage

    def on_damaged(self, damage, attacker):
        pass
