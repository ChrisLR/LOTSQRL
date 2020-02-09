from lotsqrl.evolutions.base import EvolutionNode


def brood_nodes():
    egg_sac = EvolutionNode(
        name="Egg Sac", cost=5,
        description="Allows you to lay multiple eggs in quick succession.",
    )
    nourishing_cocoon = EvolutionNode(
        name="Nourishing Cocoon",
        description="You can spin a spiderling into a self sufficient cocoon.",
        cost=10,
        requires=[egg_sac]
    )
    enhance_minion = EvolutionNode(
        name="Enhance Minion", cost=20,
        description="You can spin a Spider into another cocoon, enhancing it further.",
        requires=[egg_sac, nourishing_cocoon]
    )
    strong_web = EvolutionNode(
        name="Strong Web", cost=5,
        description="The range of your webs increase to 10 tiles",
    )
    web_wall = EvolutionNode(
        name="Web Wall", cost=10,
        description="Spin a strong web trap that will hold enemies helpless until freed.",
        requires=[strong_web]
    )
    choking_web = EvolutionNode(
        name="Choking Web", cost=20,
        description="Your webs are now covered in choking powder and helpless enemies will choke to death.",
        requires=[strong_web, web_wall]
    )
    telepath = EvolutionNode(
        name="Telepath", cost=5,
        description="Become psychic and able to recall your minions to you.",
    )
    mind_scream = EvolutionNode(
        name="Mind Scream", cost=10,
        description="You are able to scream into the mind of an enemy at great range, stunning them.",
        requires=[telepath]
    )
    mind_shatter = EvolutionNode(
        name="Mind Shatter", cost=20,
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