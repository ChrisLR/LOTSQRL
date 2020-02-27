from enum import IntEnum

from bearlibterminal import terminal


class MessageScope(IntEnum):
    TargetsPlayer = 0  # Only logs when the Actor or Target is the player
    All = 1   # Always Log


class MessageScopePreference(IntEnum):
    Default = 0  # Logs messages by default scope
    All = 1  # Logs ALL messages no matter their scope


class Messaging(object):
    _no_targets = tuple()

    def __init__(self, game, msg_scope_pref, silent=False):
        self.game = game
        self.messages = []
        self.msg_scope_pref = msg_scope_pref
        self.silent = silent

    def add_system_message(self, message, show_now=False):
        if self.silent:
            return

        self.messages.append(message)
        if show_now:
            self.game.scene.update_messages()
            terminal.refresh()

    def add_player_message(self, message, actor):
        if self.silent:
            return

        if actor is self.game.player:
            self.messages.append(message)

    def add_scoped_message(self, message_actor=None, message_target=None, message_others=None, show_now=False,
                           scope=MessageScope.TargetsPlayer, actor=None, target=None, targets=None):
        if self.silent:
            return

        if targets is None:
            targets = self._no_targets

        in_scope = self._check_scope(scope, actor, target, targets)
        if not in_scope:
            return

        player = self.game.player
        if actor is player:
            if message_actor:
                self.messages.append(message_actor)
        elif target is player or player in targets:
            if message_target:
                self.messages.append(message_target)
        else:
            if message_others:
                self.messages.append(message_others)

        if show_now:
            self.game.scene.update_messages()
            terminal.refresh()

    def _check_scope(self, scope, actor=None, target=None, targets=None):
        if self.msg_scope_pref == MessageScopePreference.All or scope == MessageScope.All:
            return True
        elif scope == MessageScope.TargetsPlayer:
            if actor is self.game.player or target is self.game.player or self.game.player in targets:
                return True
