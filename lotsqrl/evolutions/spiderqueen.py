from lotsqrl.evolutions.base import EvolutionPlan, EvolutionNode


# TODO Make Plan Flatter, reduces complexity and increases visibility.

def create_spider_queen_evolution():
    abyssal = abyssal_nodes()
    brood = brood_nodes()
    rotting = rotting_nodes()
    abyssal.add_exclude(brood)
    abyssal.add_exclude(rotting)
    brood.add_exclude(abyssal)
    brood.add_exclude(rotting)
    rotting.add_exclude(abyssal)
    rotting.add_exclude(brood)

    plan = EvolutionPlan([abyssal, brood, rotting])

    return plan


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
        description="Grow into a monstrous size.\n"
                    "Doubles starting and max health",
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


def brood_nodes():
    brood = EvolutionNode(
        name="Brood Mother",
        description="Prime descendant of the fiercest broods of spiders.\n"
                    "Born to dominate, consume and spawn an army to bring them all to their knees.\n"
                    "This one of a kind Queen must be cautious not to be surrounded by enemies\n"
                    "and let her minions die for her.",
        cost=1,
    )
    egg_sac = EvolutionNode(
        name="Egg Sac", cost=5,
        description="Allows you to lay multiple eggs in quick succession.",
    )
    nourishing_cocoon = EvolutionNode(
        name="Nourishing Cocoon",
        description="You can spin a spiderling into a self sufficient cocoon.",
        cost=5,
    )
    enhance_minion = EvolutionNode(
        name="Enhance Minion", cost=5,
        description="You can spin a Spider into another cocoon, enhancing it further.",
    )
    egg_sac.add_child(nourishing_cocoon)
    nourishing_cocoon.add_child(enhance_minion)

    strong_web = EvolutionNode(
        name="Strong Web", cost=5,
        description="The range of your webs increase to 10 tiles",
    )
    web_wall = EvolutionNode(
        name="Web Wall", cost=5,
        description="Spin a strong web trap that will hold enemies helpless until freed.",
    )
    choking_web = EvolutionNode(
        name="Choking Web", cost=5,
        description="Your webs are now covered in choking powder and helpless enemies will choke to death.",
    )
    strong_web.add_child(web_wall)
    web_wall.add_child(choking_web)

    telepath = EvolutionNode(
        name="Telepath", cost=5,
        description="Become psychic and able to recall your minions to you.",
    )
    mind_scream = EvolutionNode(
        name="Mind Scream", cost=5,
        description="You are able to scream into the mind of an enemy at great range, stunning them.",
    )
    mind_shatter = EvolutionNode(
        name="Mind Shatter", cost=5,
        description="Shatter your opponent's mind, leaving them permanently disabled.",
    )
    telepath.add_child(mind_scream)
    mind_scream.add_child(mind_shatter)

    brood.add_child(egg_sac)
    brood.add_child(strong_web)
    brood.add_child(telepath)

    return brood


def rotting_nodes():
    rotting = EvolutionNode(
        name="Rotting Spider",
        description="A necrotic spider reanimated by unholy powers.\n"
                    "It is quite weak in melee but will rain death from afar.\n"
                    "This terrifying creature can only birth parasites which are injected\n"
                    "directly into its victims.\n",
        cost=1,
    )
    bile_spit = EvolutionNode(
        name="Bile Spit", cost=5,
        description="Allows you to spit thick bile into enemies, stunning them for a few rounds.",
    )
    venomous_spit = EvolutionNode(
        name="Venomous Spit",
        description="Spitting now poisons enemies instead, damning them to a slow death.",
        cost=5,
    )
    acidic_spit = EvolutionNode(
        name="Acidic Spit", cost=5,
        description="Your spit is now burning acid, making enemies mad with pain causing them to berserk.",
    )
    bile_spit.add_child(venomous_spit)
    venomous_spit.add_child(acidic_spit)

    corpse_bomb = EvolutionNode(
        name="Corpse Bomb", cost=5,
        description="Condense Necrotic energies into a corpse, making it explode killing any nearby.",
    )
    corpse_walk = EvolutionNode(
        name="Corpse Walk", cost=5,
        description="Entering a nearby corpse allows you to teleport to any other within the map.",
    )
    animate_corpse = EvolutionNode(
        name="Animate Corpse", cost=5,
        description="You are able to reanimate corpses, making them great meat shields.",
    )
    corpse_bomb.add_child(corpse_walk)
    corpse_walk.add_child(animate_corpse)

    winged_parasites = EvolutionNode(
        name="Winged Parasites", cost=5,
        description="You can now launch your parasites straight into your victims from a distance.",
    )
    rotting_spores = EvolutionNode(
        name="Rotting Spores", cost=5,
        description="Infested enemies now exhale rotting spores, damaging any nearby enemies.",
    )
    flight_of_decay = EvolutionNode(
        name="Flight of Decay", cost=5,
        description="Your parasites now leave a trail of rotting spores behind, "
                    "rapidly killing any foe breathing it.",
    )
    winged_parasites.add_child(rotting_spores)
    rotting_spores.add_child(flight_of_decay)

    rotting.add_child(bile_spit)
    rotting.add_child(corpse_bomb)
    rotting.add_child(winged_parasites)

    return rotting
