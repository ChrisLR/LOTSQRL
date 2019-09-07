from lotsqrl.tests.utils.game import GameController
from lotsqrl.actors.goblins import Goblin


if __name__ == '__main__':
    game = GameController(starting_actors=[
        Goblin(None, 0, 6),
        Goblin(None, 0, 5),
        Goblin(None, 0, 4),
    ])
    game.start()
