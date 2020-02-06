from lotsqrl.evolutions.base import EvolutionPlan, EvolutionNode


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
    giant = EvolutionNode(
        name="Giant", cost=5,
        description="Grow into a monstrous size.\n"
                    "Doubles starting and max health",
    )
    devouring_maw = EvolutionNode(
        name="Devouring Maw",
        description="Killing an enemy consumes it instantly",
        cost=5,
        requires=[giant]
    )
    swallow_whole = EvolutionNode(
        name="Swallow Whole", cost=5,
        description="Swallow a live enemy, regenerating as you digest it",
        requires=[giant, devouring_maw]
    )
    thick_chitin = EvolutionNode(
        name="Thick Chitin", cost=5,
        description="Your chitin is tough, damage is reduced by half.",
    )
    spiked_chitin = EvolutionNode(
        name="Spiked Chitin", cost=5,
        description="Spikes now cover your body and enemies will hurt themselves with every attack",
        requires=[thick_chitin]
    )
    poisonous_hairs = EvolutionNode(
        name="Poisonous Hairs", cost=5,
        description="Any creature stupid enough to attack you will fatally poison themselves.",
        requires=[thick_chitin, spiked_chitin]
    )
    razor_pincers = EvolutionNode(
        name="Razor Pincers", cost=5,
        description="Attacking a creature will also attack those adjacent to you and your target",
    )
    bladed_legs = EvolutionNode(
        name="Bladed Legs", cost=5,
        description="Every attack you make will also damage any adjacent creatures",
        requires=[razor_pincers]
    )
    hellish_charge = EvolutionNode(
        name="Hellish Charge", cost=5,
        description="Charge in a direction, bringing death to any creature in your path.",
        requires=[razor_pincers, bladed_legs]
    )

    abyssal = EvolutionNode(
        name="Abyssal Spider",
        description="A spider brought from the deepest pits of a nameless abyss.\n"
                    "It has the strength to overpower and consume all who opposes it.\n"
                    "Luckily for the humanoids, it cannot reproduce without the hellish influences\n"
                    "of the black pit, merely birthing vampiric abyssal flies.",
        cost=1,
        children=[
            giant,
            devouring_maw,
            swallow_whole,
            thick_chitin,
            spiked_chitin,
            poisonous_hairs,
            razor_pincers,
            bladed_legs,
            hellish_charge,
        ]
    )

    return abyssal


def brood_nodes():
    egg_sac = EvolutionNode(
        name="Egg Sac", cost=5,
        description="Allows you to lay multiple eggs in quick succession.",
    )
    nourishing_cocoon = EvolutionNode(
        name="Nourishing Cocoon",
        description="You can spin a spiderling into a self sufficient cocoon.",
        cost=5,
        requires=[egg_sac]
    )
    enhance_minion = EvolutionNode(
        name="Enhance Minion", cost=5,
        description="You can spin a Spider into another cocoon, enhancing it further.",
        requires=[egg_sac, nourishing_cocoon]
    )
    strong_web = EvolutionNode(
        name="Strong Web", cost=5,
        description="The range of your webs increase to 10 tiles",
    )
    web_wall = EvolutionNode(
        name="Web Wall", cost=5,
        description="Spin a strong web trap that will hold enemies helpless until freed.",
        requires=[strong_web]
    )
    choking_web = EvolutionNode(
        name="Choking Web", cost=5,
        description="Your webs are now covered in choking powder and helpless enemies will choke to death.",
        requires=[strong_web, web_wall]
    )
    telepath = EvolutionNode(
        name="Telepath", cost=5,
        description="Become psychic and able to recall your minions to you.",
    )
    mind_scream = EvolutionNode(
        name="Mind Scream", cost=5,
        description="You are able to scream into the mind of an enemy at great range, stunning them.",
        requires=[telepath]
    )
    mind_shatter = EvolutionNode(
        name="Mind Shatter", cost=5,
        description="Shatter your opponent's mind, leaving them permanently disabled.",
        requires=[telepath, mind_scream]
    )

    brood = EvolutionNode(
        name="Brood Mother",
        description="Prime descendant of the fiercest broods of spiders.\n"
                    "Born to dominate, consume and spawn an army to bring them all to their knees.\n"
                    "This one of a kind Queen must be cautious not to be surrounded by enemies\n"
                    "and let her minions die for her.",
        cost=1,
        children=[
            egg_sac,
            nourishing_cocoon,
            enhance_minion,
            strong_web,
            web_wall,
            choking_web,
            telepath,
            mind_scream,
            mind_shatter,
        ]
    )

    return brood


def rotting_nodes():
    bile_spit = EvolutionNode(
        name="Bile Spit", cost=5,
        description="Allows you to spit thick bile into enemies, stunning them for a few rounds.",
    )
    venomous_spit = EvolutionNode(
        name="Venomous Spit",
        description="Spitting now poisons enemies instead, damning them to a slow death.",
        cost=5,
        requires=[bile_spit]
    )
    acidic_spit = EvolutionNode(
        name="Acidic Spit", cost=5,
        description="Your spit is now burning acid, making enemies mad with pain causing them to berserk.",
        requires=[bile_spit, venomous_spit]
    )
    corpse_bomb = EvolutionNode(
        name="Corpse Bomb", cost=5,
        description="Condense Necrotic energies into a corpse, making it explode killing any nearby.",
    )
    corpse_walk = EvolutionNode(
        name="Corpse Walk", cost=5,
        description="Entering a nearby corpse allows you to teleport to any other within the map.",
        requires=[corpse_bomb]
    )
    animate_corpse = EvolutionNode(
        name="Animate Corpse", cost=5,
        description="You are able to reanimate corpses, making them great meat shields.",
        requires=[corpse_bomb, corpse_walk]
    )
    winged_parasites = EvolutionNode(
        name="Winged Parasites", cost=5,
        description="You can now launch your parasites straight into your victims from a distance.",
    )
    rotting_spores = EvolutionNode(
        name="Rotting Spores", cost=5,
        description="Infested enemies now exhale rotting spores, damaging any nearby enemies.",
        requires=[winged_parasites]
    )
    flight_of_decay = EvolutionNode(
        name="Flight of Decay", cost=5,
        description="Your parasites now leave a trail of rotting spores behind, "
                    "rapidly killing any foe breathing it.",
        requires=[winged_parasites, rotting_spores]
    )

    rotting = EvolutionNode(
        name="Rotting Spider",
        description="A necrotic spider reanimated by unholy powers.\n"
                    "It is quite weak in melee but will rain death from afar.\n"
                    "This terrifying creature can only birth parasites which are injected\n"
                    "directly into its victims.\n",
        cost=1,
        children=[
            winged_parasites,
            rotting_spores,
            flight_of_decay,
            corpse_bomb,
            corpse_walk,
            animate_corpse,
            bile_spit,
            venomous_spit,
            acidic_spit,
        ]
    )

    return rotting
