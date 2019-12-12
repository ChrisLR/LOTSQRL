from lotsqrl import teams


class Filter(object):
    def filter(self, actor, targets):
        return targets


class OnlyEnemies(Filter):
    # TODO This relation does not belong here
    alliance_map = {
        teams.Team.SpiderQueen: teams.Team.Goblin,
        teams.Team.Goblin: teams.Team.SpiderQueen
    }

    def filter(self, actor, targets):
        enemy_team = self.alliance_map.get(actor.team)
        return filter(lambda t: t.team == enemy_team, targets)


class OnlyCorpses(Filter):
    def filter(self, actor, targets):
        corpse_team = teams.Team.Corpse
        return filter(lambda t: t.team == corpse_team, targets)


class OnlyCocoons(Filter):
    def filter(self, actor, targets):
        cocoon_type = teams.ActorTypes.Cocoon
        return filter(lambda t: t.actor_type == cocoon_type, targets)
