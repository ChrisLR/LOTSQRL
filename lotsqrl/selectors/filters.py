from lotsqrl import teams, utils


class Filter(object):
    def filter(self, actor, targets):
        return targets


class OnlyEnemies(Filter):
    def filter(self, actor, targets):
        return filter(lambda t: utils.is_enemy(actor, t), targets)


class OnlyAllies(Filter):
    def filter(self, actor, targets):
        return filter(lambda t: utils.is_allied(actor, t), targets)


class OnlyCorpses(Filter):
    def filter(self, actor, targets):
        corpse_team = teams.Team.Corpse
        return filter(lambda t: t.team == corpse_team, targets)


class OnlyCocoons(Filter):
    def filter(self, actor, targets):
        cocoon_type = teams.ActorTypes.Cocoon
        return filter(lambda t: t.actor_type == cocoon_type, targets)
