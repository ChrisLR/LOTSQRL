from enum import IntEnum


class Team(IntEnum):
    QueenSpider = 0
    Goblin = 1
    Corpse = 2


class ActorTypes(IntEnum):
    Corpse = 0
    Egg = 1
    Cocoon = 2
    Spiderling = 3
    Spider = 4
    QueenSpider = 5
    Goblin = 6
    GoblinChief = 7
