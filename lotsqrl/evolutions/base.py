class EvolutionPlan(object):
    def __init__(self, nodes):
        self.nodes = nodes
        self._nodes = {node.name: node for node in nodes} if nodes else {}

    def get_root_node(self, name):
        return self._nodes[name]


class EvolutionNode(object):
    def __init__(self, name, description, cost, children=None, excludes=None, requires=None):
        self.name = name
        self.description = description
        self.cost = cost
        self.children = children or []
        self._children = {child.name: child for child in children} if children else {}
        self.excludes = excludes or []
        self.requires = requires or []

    def add_child(self, node):
        self.children.append(node)
        self._children[node.name] = node

    def add_exclude(self, node):
        self.excludes.append(node)

    def get_child_node(self, name):
        return self._children[name]
