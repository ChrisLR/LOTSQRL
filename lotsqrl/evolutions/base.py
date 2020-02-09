class EvolutionPlan(object):
    def __init__(self, nodes):
        self.nodes = nodes
        self._nodes = {node.evolution.name: node for node in nodes} if nodes else {}

    def get_root_node(self, name):
        return self._nodes[name]


class EvolutionNode(object):
    def __init__(self, evolution, children=None, excludes=None, requires=None):
        self.evolution = evolution
        self.children = children or []
        self._children = {child.evolution.name: child for child in children} if children else {}
        self.excludes = excludes or []
        self.requires = requires or []

    def add_child(self, node):
        self.children.append(node)
        self._children[node.evolution.name] = node

    def add_exclude(self, node):
        self.excludes.append(node)

    def get_child_node(self, name):
        return self._children[name]


class Evolution(object):
    name = ""
    description = ""
    cost = 0

    def __init__(self, host):
        self.host = host
        self.on_apply()

    def on_apply(self):
        pass

    def on_remove(self):
        pass
