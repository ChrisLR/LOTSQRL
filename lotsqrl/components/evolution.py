class Evolution(object):
    def __init__(self, host, plan, points=0):
        self.host = host
        self.plan = plan
        self.evolved_map = {}
        self.points = points

    def add(self, points):
        self.points += points

    def remove(self, points):
        self.points -= points

    def consume(self, target):
        amount = target.evolution_worth
        evolution = target.evolution
        if evolution is not None:
            self.add(amount + evolution.points)
        else:
            self.add(amount)

    def has_evolution(self, name):
        return self.evolved_map.get(name, False)
