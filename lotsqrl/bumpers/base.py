from lotsqrl import utils


class Bumper(object):
    def __init__(self, host):
        self.host = host

    def bump(self, target):
        pass


class Null(Bumper):
    pass


class Basic(Bumper):
    def __init__(self, host, attack_name):
        super().__init__(host)
        self.attack_name = attack_name

    def bump(self, target):
        if not target.dead and utils.is_enemy(self.host, target):
            self.host.actions.try_execute(self.attack_name, target)
