class Selector(object):
    def __init__(self, message=None, filters=None):
        self.filters = filters
        self.message = message

    def get(self, actor):
        self.show_message(actor)

    def _filter(self, actor, targets):
        if not self.filters:
            return targets

        filtered_targets = targets
        for filter in self.filters:
            filtered_targets = filter.filter(actor, filtered_targets)

        return filtered_targets

    def show_message(self, actor):
        if self.message:
            actor.game.add_message(self.message, show_now=True)
