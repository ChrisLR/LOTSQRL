from functools import partial

from bearlibterminal import terminal


class StaticLabel(object):
    def __init__(self, text, x, y):
        self.text = text
        self.x = x
        self.y = y

    def draw(self):
        terminal.printf(self.x, self.y, self.text)


class DynamicLabel(object):
    def __init__(self, getter, x, y):
        self.getter = getter
        self.x = x
        self.y = y

    def draw(self):
        text = str(self.getter())
        terminal.printf(self.x, self.y, text)


class Tree(object):
    CHAR_SET = "abcdefghijklmnopqrstuvwxyz0123456789"

    def __init__(self, plan):
        self.origin_x = 0
        self.origin_y = 3
        self.sub_nodes = {}
        self.root_nodes = {}
        self.keys = (c for c in self.CHAR_SET)
        self.selected_root_node = None
        self.selected_sub_node = None
        self.root_max_width = max(len(node.name) for node in plan.nodes) + 5
        self.sub_node_max_width = 0

        row = self.origin_y
        for node in plan.nodes:
            root_node = TreeNode(node, self.origin_x, row, next(self.keys))
            self.root_nodes[root_node.key] = root_node
            self.sub_nodes[root_node] = {}
            self._create_sub_nodes(root_node, self.root_max_width)
            row += 1

        self.select_root_node("a")
        for root, sub_nodes in self.sub_nodes.items():
            max_sub_width = max(len(node.node.name) for node in sub_nodes.values())
            if max_sub_width > self.sub_node_max_width:
                self.sub_node_max_width = max_sub_width
        self.sub_node_max_width += self.root_max_width + 1

    def select_root_node(self, key):
        root_node = self.root_nodes[key]
        self.selected_root_node = root_node
        self.selected_sub_node = self.sub_nodes[root_node]["a"]

    def select_sub_node(self, key):
        self.selected_sub_node = self.sub_nodes[self.selected_root_node][key]

    def _create_sub_nodes(self, root_node, root_max_width):
        row = self.origin_y
        column_space = root_max_width
        sub_keys = (c for c in self.CHAR_SET)
        for sub_node in root_node.node.children:
            sub_key = next(sub_keys)
            new_tree_node = TreeNode(sub_node, column_space, row, sub_key)
            self.sub_nodes[root_node][sub_key] = new_tree_node
            row += 1

    def draw(self):
        for node in self.root_nodes.values():
            node.draw()

        for sub_node in self.sub_nodes[self.selected_root_node].values():
            sub_node.draw()


class TreeNode(object):
    def __init__(self, node, x, y, key):
        self.node = node
        self.x = x
        self.y = y
        self.key = key
        self.draw_string = f"{self.key}) {self.node.name}"

    def draw(self):
        terminal.printf(self.x, self.y, self.draw_string)


def get_sub_node_attribute(tree, attribute):
    return getattr(tree.selected_sub_node.node, attribute)


class EvolutionScene(object):
    def __init__(self, actor):
        self.actor = actor
        self.tree = Tree(self.actor.evolution.plan)
        sub_node_max_width = self.tree.sub_node_max_width
        self.ui_elements = [
            StaticLabel("Category", 0, 0),
            StaticLabel("Abilities", self.tree.root_max_width, 0),
            StaticLabel("Name:", sub_node_max_width, 1),
            DynamicLabel(partial(get_sub_node_attribute, self.tree, 'name'), sub_node_max_width + 5, 1),
            StaticLabel("Cost:", sub_node_max_width, 2),
            DynamicLabel(partial(get_sub_node_attribute, self.tree, 'cost'), sub_node_max_width + 5, 2),
            StaticLabel("Description:", sub_node_max_width, 3),
            DynamicLabel(partial(get_sub_node_attribute, self.tree, 'description'), sub_node_max_width + 5, 4)
        ]

    def draw(self):
        terminal.clear()
        self.tree.draw()
        for ui_element in self.ui_elements:
            ui_element.draw()
        terminal.refresh()

    def update(self, terminal_input):
        pass

    def start(self):
        self.draw()
        must_stop = False
        while not must_stop:
            terminal_input = terminal.read()
            if terminal_input == terminal.TK_CLOSE:
                must_stop = True
            else:
                self.update(terminal_input)


if __name__ == '__main__':
    from lotsqrl.actors import spiders
    running = terminal.open()
    terminal.set("window: size=100x50, title=Meh")
    actor = spiders.SpiderQueen(None, 0, 0)
    scene = EvolutionScene(actor)
    scene.start()
    terminal.close()
