class Selector(object):
    def __init__(self, message=None, filters=None):
        self.filters = filters
        self.message = message

    def get(self, actor):
        pass

    def _filter(self, actor, targets):
        filtered_targets = targets
        for filter in self.filters:
            filtered_targets = filter.filter(actor, filtered_targets)

        return filtered_targets

    def show_message(self, actor):
        if self.message:
            actor.game.add_message(self.message, show_now=True)
