from lotsqrl.bumpers.base import Basic
from lotsqrl.teams import ActorTypes


class EggBurrower(Basic):
    def bump(self, target):
        if target.actor_type == ActorTypes.Cocoon and not target.burrowed:
            return self.host.actions.try_execute("burrow_egg", target)

        return super().bump(target)
