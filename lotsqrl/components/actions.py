from bearlibterminal import terminal


class Action(object):
    def __init__(self, host, base_actions):
        self.host = host
        self.actions = {action.name: action for action in base_actions}

    def can_execute(self, name, target=None):
        """Confirms if an action CAN execute
        Useful we need to know if an action MAY occur at all

        :param name: Name of the Action
        :param target: Target Actor
        :return: Bool telling if action CAN execute
        """
        action = self.actions.get(name)
        if action is not None:
            return action.can_execute(self.host, target)

    def execute(self, name, target=None):
        """Executes an action
        Useful we need to differentiate the result from the occurrence

        :param name: Name of the Action
        :param target: Target Actor
        :return: Bool telling if action succeeded
        """
        action = self.actions.get(name)
        if action is not None:
            return action.execute(self.host, target)

    def get(self, name):
        return self.actions.get(name)

    def try_execute(self, name, target=None):
        """Tries to execute and executes in one step.
        Useful when a failed action is the same as an action that could not execute

        :param name: Name of the Action
        :param target: Target Actor
        :return: Bool telling if action occurred
        """
        action = self.actions.get(name)
        if action is not None:
            if target is None and action.selectors and self.host.is_player:
                targets = []
                for selector in action.selectors:
                    result = selector.get(self.host)
                    if result is terminal.TK_INPUT_CANCELLED:
                        self.host.game.messaging.add_system_message("Cancelled.")
                        return False
                    else:
                        targets.extend(result)

                if action.targets == 1:
                    target = targets[0] if targets else None
                else:
                    target = targets

            host = self.host
            can_execute = action.can_execute(host, target)
            if can_execute:
                result = action.execute(host, target)
                return result
            return can_execute
