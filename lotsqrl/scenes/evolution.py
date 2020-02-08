from bearlibterminal import terminal

from lotsqrl.ui import utils
from lotsqrl.ui.base import UIElement
from lotsqrl.ui.labels import Label, DynamicLabel
from lotsqrl.ui.themes import Theme, default_theme


class Tree(object):
    CHAR_SET = "abcdefghijklmnopqrstuvwxyz0123456789"

    def __init__(self, plan, actor):
        self.origin_x = 0
        self.origin_y = 3
        self.sub_nodes = {}
        self.root_nodes = {}
        self.keys = (c for c in self.CHAR_SET)
        self.selected_root_node = None
        self.selected_sub_node = None
        self.selected_node = None
        self.root_max_width = max(len(node.name) for node in plan.nodes) + 5
        self.sub_node_max_width = 0
        self.actor = actor
        self.purchased_theme = Theme(active_color="black", active_bg_color="green", inactive_color="green")
        self.locked_theme = Theme(active_color="black", active_bg_color="red", inactive_color="red")

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
        root_node = self.root_nodes.get(key)
        if not root_node:
            return

        # TODO Could use a UIElement Grouping that tracks what is active instead.
        if self.selected_node:
            self.selected_node.is_active = False

        self.selected_root_node = root_node
        self.selected_node = root_node
        self.selected_node.is_active = True

    def select_sub_node(self, key):
        sub_node = self.sub_nodes[self.selected_root_node].get(key)
        if not sub_node:
            return

        if self.selected_node:
            self.selected_node.is_active = False

        self.selected_sub_node = sub_node
        self.selected_node = sub_node
        self.selected_node.is_active = True

    def _create_sub_nodes(self, root_node, root_max_width):
        row = self.origin_y
        column_space = root_max_width
        sub_keys = (c for c in self.CHAR_SET)
        for sub_node in root_node.node.children:
            sub_key = next(sub_keys)

            has_evolution = self.actor.evolution.has_evolution(sub_node.name)
            if has_evolution:
                theme = self.purchased_theme
            else:
                can_purchase = self.actor.evolution.can_purchase(root_node.node.name, sub_node.name)
                theme = None if can_purchase else self.locked_theme

            theme = theme
            new_tree_node = TreeNode(sub_node, column_space, row, sub_key, theme=theme)
            self.sub_nodes[root_node][sub_key] = new_tree_node
            row += 1

    def draw(self):
        for node in self.root_nodes.values():
            node.draw()

        for sub_node in self.sub_nodes[self.selected_root_node].values():
            sub_node.draw()

    def get_selected_root_node(self):
        return self.selected_root_node

    def get_selected_sub_node(self):
        return self.selected_sub_node

    def get_selected_node(self):
        return self.selected_node

    def purchase(self):
        root_node = self.selected_root_node.node if self.selected_root_node else None
        sub_node = self.selected_sub_node.node if self.selected_sub_node else None
        root_name = root_node.name if root_node else None
        sub_name = sub_node.name if sub_node else None
        self.actor.evolution.purchase(root_name, sub_name)
        self.update_node_themes()

    def update_node_themes(self):
        actor = self.actor
        for root_node, sub_nodes in self.sub_nodes.items():
            for sub_node in sub_nodes.values():
                has_evolution = actor.evolution.has_evolution(sub_node.node.name)
                if has_evolution:
                    theme = self.purchased_theme
                else:
                    can_purchase = actor.evolution.can_purchase(root_node.node.name, sub_node.node.name)
                    theme = default_theme if can_purchase else self.locked_theme

                theme = theme
                sub_node.theme = theme

            has_evolution = actor.evolution.has_evolution(root_node.node.name)
            if has_evolution:
                theme = self.purchased_theme
            else:
                can_purchase = actor.evolution.can_purchase(root_node.node.name)
                theme = default_theme if can_purchase else self.locked_theme

            theme = theme
            root_node.theme = theme


class TreeNode(UIElement):
    def __init__(self, node, rel_x, rel_y, key, theme=None):
        super().__init__(None, rel_x, rel_y, theme=theme)
        self.node = node
        self.key = key
        self.text = f"{self.key}) {self.node.name}"

    def draw(self):
        colorized_string = utils.colorize_text(self, self.text)
        terminal.printf(self.x, self.y, colorized_string)


def get_node_attribute(tree, attribute):
    def _get_node_attribute():
        node = tree.get_selected_node()
        return getattr(node.node, attribute)
    return _get_node_attribute


class EvolutionScene(object):
    FOCUS_ROOT = 0
    FOCUS_SUB = 1

    def __init__(self, actor):
        self.actor = actor
        self.tree = Tree(self.actor.evolution.plan, actor)
        sub_node_max_width = self.tree.sub_node_max_width
        tab_theme = Theme(active_color="black", active_bg_color="yellow")
        self.category_label = Label(text="Category", rel_x=0, rel_y=0, theme=tab_theme)
        self.abilities_label = Label(text="Abilities", rel_x=self.tree.root_max_width, rel_y=0, theme=tab_theme)
        self.ui_elements = [
            self.category_label,
            self.abilities_label,
            Label(text="Name:", rel_x=sub_node_max_width, rel_y=1),
            DynamicLabel(get_node_attribute(self.tree, 'name'), rel_x=sub_node_max_width + 5, rel_y=1),
            Label(text="Cost:", rel_x=sub_node_max_width, rel_y=2),
            DynamicLabel(get_node_attribute(self.tree, 'cost'), rel_x=sub_node_max_width + 5, rel_y=2),
            Label(text="Description:", rel_x=sub_node_max_width, rel_y=3),
            DynamicLabel(get_node_attribute(self.tree, 'description'), rel_x=sub_node_max_width + 5, rel_y=4)
        ]
        self.selected_column = self.FOCUS_ROOT
        self.category_label.is_active = True
        self.abilities_label.is_active = False
        self.must_stop = True

    def draw(self):
        terminal.clear()

        self.tree.draw()
        for ui_element in self.ui_elements:
            ui_element.draw()
        terminal.refresh()

    def update(self, terminal_input):
        if terminal_input == terminal.TK_TAB:
            self.swap_column_focus()
            return

        if terminal_input == terminal.TK_ENTER:
            self.tree.purchase()

        if terminal_input == terminal.TK_ESCAPE:
            self.actor.game.evolution_scene_active = False
            self.must_stop = True

        char_key = chr(terminal.state(terminal.TK_WCHAR))
        if self.selected_column == self.FOCUS_ROOT:
            self.tree.select_root_node(char_key)
        elif self.selected_column == self.FOCUS_SUB:
            self.tree.select_sub_node(char_key)

    def swap_column_focus(self):
        if self.selected_column == self.FOCUS_ROOT:
            self.selected_column = self.FOCUS_SUB
            self.abilities_label.is_active = True
            self.category_label.is_active = False
        elif self.selected_column == self.FOCUS_SUB:
            self.selected_column = self.FOCUS_ROOT
            self.category_label.is_active = True
            self.abilities_label.is_active = False

    def start(self):
        self.must_stop = False

        while not self.must_stop:
            terminal.layer(0)
            self.draw()
            terminal_input = terminal.read()
            if terminal_input == terminal.TK_CLOSE:
                self.must_stop = True
            else:
                self.update(terminal_input)
