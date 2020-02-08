from lotsqrl.actors.spiders import SpiderQueen
from lotsqrl.actors.goblins import Goblin
from lotsqrl.teams import Team


def test_killing_and_eating_corpse_transfers_evolution(fake_game):
    level = fake_game.level
    spider = SpiderQueen(fake_game, 0, 0)
    goblin = Goblin(fake_game, 0, 0)
    level.add_actor(spider)
    level.add_actor(goblin)
    goblin.evolution_worth = 6
    goblin.on_death()
    corpse = fake_game.level.get_actors_by_team(Team.Corpse)[0]
    spider.actions.execute("eat_corpse", target=corpse)

    assert corpse.evolution_worth == 6
    assert spider.evolution.points == 6
