from lotsqrl import armors
from lotsqrl.actors.goblins import Goblin
from lotsqrl.actors.spiders import SpiderQueen


def test_attacking_with_armor_reduces_damage(fake_game):
    level = fake_game.level
    spider = SpiderQueen(fake_game, 0, 0)
    goblin = Goblin(fake_game, 0, 0)
    level.add_actor(spider)
    level.add_actor(goblin)
    spider.evolution.points = 666
    spider.armor.set(armors.ThickChitin)
    goblin.actions.actions["stab"].damage = (2, 2)
    spider_hp = spider.health.hp
    goblin.actions.execute('stab', spider)

    assert spider.health.hp == spider_hp - 1


def test_attacking_with_spiked_armor_retaliates_damage(fake_game):
    level = fake_game.level
    spider = SpiderQueen(fake_game, 0, 0)
    goblin = Goblin(fake_game, 0, 0)
    level.add_actor(spider)
    level.add_actor(goblin)
    spider.evolution.points = 666
    spider.armor.set(armors.SpikedChitin)
    goblin_hp = goblin.health.hp
    goblin.actions.execute('stab', spider)

    assert goblin.health.hp == goblin_hp - 2


def test_attacking_with_poisonous_armor_sets_poison_effect(fake_game):
    level = fake_game.level
    spider = SpiderQueen(fake_game, 0, 0)
    goblin = Goblin(fake_game, 0, 0)
    level.add_actor(spider)
    level.add_actor(goblin)
    spider.evolution.points = 666
    spider.armor.set(armors.PoisonousHairs)
    goblin.actions.execute('stab', spider)

    assert goblin.effects.get_by_name("poison")
