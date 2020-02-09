from lotsqrl.evolutions.abyssal import abyssal_nodes
from lotsqrl.evolutions.base import EvolutionPlan
#from lotsqrl.evolutions.brood import brood_nodes
#from lotsqrl.evolutions.rotting import rotting_nodes


def create_spider_queen_evolution():
    abyssal = abyssal_nodes()
    #brood = brood_nodes()
    #rotting = rotting_nodes()
    #abyssal.add_exclude(brood)
    #abyssal.add_exclude(rotting)
    #brood.add_exclude(abyssal)
    #brood.add_exclude(rotting)
    r#otting.add_exclude(abyssal)
    #rotting.add_exclude(brood)

    plan = EvolutionPlan([abyssal])

    return plan


