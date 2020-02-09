from lotsqrl.evolutions.base import EvolutionNode


def rotting_nodes():
    bile_spit = EvolutionNode(
        name="Bile Spit", cost=5,
        description="Allows you to spit thick bile into enemies, stunning them for a few rounds.",
    )
    venomous_spit = EvolutionNode(
        name="Venomous Spit",
        description="Spitting now poisons enemies instead, damning them to a slow death.",
        cost=10,
        requires=[bile_spit]
    )
    acidic_spit = EvolutionNode(
        name="Acidic Spit", cost=20,
        description="Your spit is now burning acid, making enemies mad with pain causing them to berserk.",
        requires=[bile_spit, venomous_spit]
    )
    corpse_bomb = EvolutionNode(
        name="Corpse Bomb", cost=5,
        description="Condense Necrotic energies into a corpse, making it explode killing any nearby.",
    )
    corpse_walk = EvolutionNode(
        name="Corpse Walk", cost=10,
        description="Entering a nearby corpse allows you to teleport to any other within the map.",
        requires=[corpse_bomb]
    )
    animate_corpse = EvolutionNode(
        name="Animate Corpse", cost=20,
        description="You are able to reanimate corpses, making them great meat shields.",
        requires=[corpse_bomb, corpse_walk]
    )
    winged_parasites = EvolutionNode(
        name="Winged Parasites", cost=5,
        description="You can now launch your parasites straight into your victims from a distance.",
    )
    rotting_spores = EvolutionNode(
        name="Rotting Spores", cost=10,
        description="Infested enemies now exhale rotting spores, damaging any nearby enemies.",
        requires=[winged_parasites]
    )
    flight_of_decay = EvolutionNode(
        name="Flight of Decay", cost=20,
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