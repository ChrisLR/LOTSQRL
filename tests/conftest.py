import pytest

from lotsqrl.game import Game
from lotsqrl import actors
from lotsqrl.messages import Messaging, MessageScope
from lotsqrl.config import MainOptions


@pytest.fixture
def fake_game():
    fake_game = FakeGame()
    fake_game.prepare()
    return fake_game


class FakeGame(Game):
    """
    Fake Game object allowing tests to control the flow and avoid using the terminal.

    Run has to be called multiple times for each *step* of the game.
    This prevents the tests being locked up by the game loop.

    No Game Events will be processed during the tests.
    The player will not have its PlayerController associated.
    """
    def __init__(self):
        self.boss = actors.GoblinChief(self, 0, 0)
        self.player = actors.SpiderQueen(self, 0, 0)
        self.camera = None
        self.game_won = False
        self.options = MainOptions()
        self.screen_info = None
        self.level = None
        self.running = False
        self.should_restart = False
        self.scene = None
        self.turn = 0
        self.messaging = Messaging(self, MessageScope.All)

    def run(self):
        level = self.level

        for actor in level.actors.copy():
            if actor.level is not None:
                actor.act()
                actor.update()
