from lotsqrl.evolutions.base import EvolutionPlan, EvolutionNode

""" 
PLANNING 

Abyssal Spider (Eggs are replaced by Abyssal Flies)
    - Giant - Devouring Maw - Swallow Whole
    - Thick Chitin - Spiked Chitin - Poisonous Hair
    - Razor pincers - Bladed Legs - Hellish Charge

Brood Mother (Typical Eggs)
    - Egg Sac - Nourishing Cocoon -  
    - Strong Web - Web Wall - Choking Web
    - Telepath - Mind Scream - Shatter Mind

Rotting Spider (Parasitic Eggs)
    - Bile Spit - Venomous Spit - Acidic spit
    - Corpse Bomb - Corpse Walk - Animate Corpse
    - Winged Parasite - Rotting Spores - Flight of Decay 
"""


def abyssal_nodes():
    abyssal = EvolutionNode(
        name="Abyssal Spider",
        description="A spider brought from the deepest pits of a nameless abyss.\n"
                    "It has the strength to overpower and consume all who opposes it.\n"
                    "Luckily for the humanoids, it cannot reproduce without the hellish influences\n"
                    "of the black pit, merely birthing vampiric abyssal flies.",
        cost=1
    )
    giant = EvolutionNode(
        name="Giant", cost=5,
        description="Grow into a monstrous size, doubles starting and max health",
    )
    devouring_maw = EvolutionNode(
        name="Devouring Maw",
        description="Killing an enemy consumes it instantly",
        cost=5,
    )
    swallow_whole = EvolutionNode(
        name="Swallow Whole", cost=5,
        description="Swallow a live enemy, regenerating as you digest it",
    )
    giant.add_child(devouring_maw)
    devouring_maw.add_child(swallow_whole)

    thick_chitin = EvolutionNode(
        name="Thick Chitin", cost=5,
        description="Your chitin is tough, damage is reduced by half.",
    )
    spiked_chitin = EvolutionNode(
        name="Spiked Chitin", cost=5,
        description="Spikes now cover your body and enemies will hurt themselves with every attack",
    )
    poisonous_hairs = EvolutionNode(
        name="Poisonous Hairs", cost=5,
        description="Any creature stupid enough to attack you will fatally poison themselves.",
    )

    thick_chitin.add_child(spiked_chitin)
    spiked_chitin.add_child(poisonous_hairs)

    razor_pincers = EvolutionNode(
        name="Razor Pincers", cost=5,
        description="Attacking a creature will also attack those adjacent to you and your target",
    )
    bladed_legs = EvolutionNode(
        name="Bladed Legs", cost=5,
        description="Every attack you make will also damage any adjacent creatures",
    )
    hellish_charge = EvolutionNode(
        name="Hellish Charge", cost=5,
        description="Charge in a direction, bringing death to any creature in your path.",
    )
    razor_pincers.add_child(bladed_legs)
    bladed_legs.add_child(hellish_charge)

    abyssal.add_child(giant)
    abyssal.add_child(thick_chitin)
    abyssal.add_child(razor_pincers)

    return abyssal


def create_spider_queen_evolution():
    abyssal = abyssal_nodes()
    brood = EvolutionNode(
        name="Brood Mother",
        description="Prime descendant of the fiercest broods of spiders.\n"
                    "Born to dominate, consume and spawn an army to bring them all to their knees.\n"
                    "This one of a kind Queen must be cautious not to be surrounded by enemies\n"
                    "and let her minions die for her.",
        cost=1,
        children=[]
    )
    rotting = EvolutionNode(
        name="Rotting Spider",
        description="A necrotic spider reanimated by unholy powers.\n"
                    "It is quite weak in melee but will rain death from afar.\n"
                    "This terrifying creature can only birth parasites which are injected\n"
                    "directly into its victims.\n",
        cost=1,
        children=[]
    )
    abyssal.add_exclude(brood)
    abyssal.add_exclude(rotting)
    brood.add_exclude(abyssal)
    brood.add_exclude(rotting)
    rotting.add_exclude(abyssal)
    rotting.add_exclude(brood)

    plan = EvolutionPlan([abyssal, brood, rotting])

    return plan



