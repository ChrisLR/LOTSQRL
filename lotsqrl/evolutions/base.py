class EvolutionPlan(object):
    def __init__(self, nodes):
        self.nodes = nodes


class EvolutionNode(object):
    def __init__(self, name, description, cost, children=None, excludes=None):
        self.name = name
        self.description = description
        self.cost = cost
        self.children = children or []
        self.excludes = excludes or []

    def add_child(self, node):
        self.children.append(node)

    def add_exclude(self, node):
        self.excludes.append(node)