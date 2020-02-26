from lotsqrl.components.base import Component


class Health(Component):
    def __init__(self, host, max_hp, hp=None):
        super().__init__(host)
        self.max_hp = max_hp
        self.hp = hp or max_hp

    def damage(self, damage, attacker=None, leave_corpse=True):
        armor = self.host.armor
        if armor is not None:
            damage = armor.reduce(damage)
            armor.on_damaged(damage, attacker)

        self.hp -= damage
        if self.hp <= 0:
            self.host.on_death(leave_corpse)
            if attacker and attacker.score:
                attacker.score.kills += 1

    def heal(self, health):
        total_hp = self.hp + health
        if total_hp >= self.max_hp:
            total_hp = self.max_hp

        self.hp = total_hp
