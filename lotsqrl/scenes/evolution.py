from bearlibterminal import terminal


class Label(object):
    def __init__(self, text, x, y):
        self.text = text
        self.x = x
        self.y = y

    def draw(self):
        terminal.printf(self.x, self.y, self.text)


class Tree(object):
    CHAR_SET = "abcdefghijklmnopqrstuvwxyz0123456789"

    def __init__(self, plan):
        self.origin_x = 0
        self.origin_y = 3
        self.sub_nodes = {}
        self.root_nodes = []
        self.keys = (c for c in self.CHAR_SET)
        self.selected_root_node = None
        self.selected_sub_node = None
        self.root_max_width = max(len(node.name) for node in plan.nodes) + 5
        self.sub_node_max_width = 0

        row = self.origin_y
        for node in plan.nodes:
            root_node = TreeNode(node, self.origin_x, row, next(self.keys))
            self.root_nodes.append(root_node)
            self.sub_nodes[root_node] = []
            self._create_sub_nodes(root_node, self.root_max_width)
            row += 1

        self.select_root_node(self.root_nodes[0])
        for root, sub_nodes in self.sub_nodes.items():
            max_sub_width = max(len(node.node.name) for node in sub_nodes)
            if max_sub_width > self.sub_node_max_width:
                self.sub_node_max_width = max_sub_width
        self.sub_node_max_width += self.root_max_width

    def select_root_node(self, root_node):
        self.selected_root_node = root_node
        self.selected_sub_node = self.sub_nodes[root_node][0]

    def _create_sub_nodes(self, root_node, root_max_width):
        row = self.origin_y
        column_space = root_max_width
        sub_keys = (c for c in self.CHAR_SET)
        for sub_node in root_node.node.children:
            new_tree_node = TreeNode(sub_node, column_space, row, next(sub_keys))
            self.sub_nodes[root_node].append(new_tree_node)
            row += 1

    def draw(self):
        for node in self.root_nodes:
            node.draw()

        for sub_node in self.sub_nodes[self.selected_root_node]:
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


class EvolutionScene(object):
    def __init__(self, actor):
        self.actor = actor
        self.tree = Tree(self.actor.evolution.plan)
        self.category_label = Label("Category", 0, 0)
        self.abilities_label = Label("Abilities", self.tree.root_max_width, 0)

    def draw(self):
        terminal.clear()
        self.tree.draw()
        self.category_label.draw()
        self.abilities_label.draw()
        terminal.printf(self.tree.sub_node_max_width, 1, f"Name: {self.tree.selected_sub_node.node.name}")


if __name__ == '__main__':
    from lotsqrl.actors import spiders
    running = terminal.open()
    terminal.set("window: title=Meh")
    terminal.clear()
    actor = spiders.SpiderQueen(None, 0, 0)
    scene = EvolutionScene(actor)
    scene.draw()
    terminal.refresh()
    while terminal.read() != terminal.TK_CLOSE:
        pass

    terminal.close()
