from bearlibterminal import terminal


class EvolutionScene(object):
    def __init__(self, actor):
        self.actor = actor

    def draw(self):
        terminal.clear()
        plan = self.actor.evolution.plan
        current_y = 1
        current_x = 1
        for node in plan.nodes:
            terminal.printf(current_x, current_y, node.name)
            current_x += len(node.name) + 1
            current_y += 1
            current_y = self.draw_sub_nodes(node, current_x, current_y)
            current_y += 1
            current_x = 1

    def draw_sub_nodes(self, parent_node, current_x, current_y):
        origin_x = current_x
        for sub_node in parent_node.children:
            terminal.printf(current_x, current_y, sub_node.name)
            current_x += len(sub_node.name) + 1
            self.draw_sub_nodes(sub_node, current_x, current_y)
            current_y += 1
            current_x = origin_x

        return current_y


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
