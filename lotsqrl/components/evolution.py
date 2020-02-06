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

    def can_purchase(self, root_name, sub_name):
        root_node = self.plan.get_root_node(root_name)
        sub_node = root_node.get_child_node(sub_name)
        has_all = all(self.evolved_map.get(requirement.name) for requirement in sub_node.requires)
        excludes_all = all(not self.evolved_map.get(requirement.name) for requirement in sub_node.excludes)

        if has_all and excludes_all:
            return True
        return False

    def purchase(self, root_name, sub_name):
        if self.evolved_map.get(sub_name):
            return  # We do not allow buying twice

        root_node = self.plan.get_root_node(root_name)
        sub_node = root_node.get_child_node(sub_name)
        if self.points >= sub_node.cost:
            self.remove(sub_node.cost)
            self.evolved_map[sub_node.name] = True
            return True
        return False
