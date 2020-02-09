from lotsqrl.components.base import Component


class Evolution(Component):
    def __init__(self, host, plan, points=0):
        super().__init__(host)
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

    def can_purchase(self, root_name, sub_name=None):
        root_node = self.plan.get_root_node(root_name)
        wanted_node = root_node
        if sub_name is not None:
            sub_node = root_node.get_child_node(sub_name)
            wanted_node = sub_node
            has_root = self.evolved_map.get(root_name)
            if not has_root:
                return False

        has_all = all(self.evolved_map.get(requirement.name) for requirement in wanted_node.requires)
        if not has_all:
            return False

        excludes_all = all(not self.evolved_map.get(requirement.name) for requirement in wanted_node.excludes)
        if not excludes_all:
            return False

        return True

    def purchase(self, root_name, sub_name=None):
        wanted_name = sub_name or root_name
        if self.evolved_map.get(wanted_name):
            return  # We do not allow buying twice

        if not self.can_purchase(root_name, sub_name):
            return False

        root_node = self.plan.get_root_node(root_name)
        wanted_node = root_node
        if sub_name is not None:
            sub_node = root_node.get_child_node(sub_name)
            wanted_node = sub_node

        if self.points >= wanted_node.cost:
            self.remove(wanted_node.cost)
            self.evolved_map[wanted_node.name] = True
            return True
        return False
