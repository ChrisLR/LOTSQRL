from lotsqrl.evolutions.base import EvolutionNode, Evolution


class Giant(Evolution):
    name = "Giant"
    cost = 5
    description = (
        "Grow into a monstrous size.\n"
        "Doubles starting and max health")

    def on_apply(self):
        host = self.host
        self.host.max_hp *= 2
        self.host.hp *= 2
        host.game.messaging.add_scoped_message(
            message_actor=f"You rapidly grow into a monstrous size!",
            message_others=f"{host.name} rapidly grows into a monstrous size!",
            actor=host
        )

    def on_remove(self):
        host = self.host
        new_max = int(round(host.max_hp / 2))
        host.max_hp = new_max
        if host.hp > new_max:
            host.hp = new_max

        host.game.messaging.add_scoped_message(
            message_actor=f"You rapidly shrink into your normal size!",
            message_others=f"{host.name} rapidly shrinks into its regular size!",
            actor=host
        )


class DevouringMaw(Evolution):
    name = "Devouring Maw",
    cost = 10
    description = "Killing an enemy consumes it instantly"


class SwallowWhole(Evolution):
    name = "Swallow Whole"
    cost = 20
    description = "Swallow a live enemy, regenerating as you digest it"


class ThickChitin(Evolution):
    name = "Thick Chitin"
    cost = 5
    description = "Your chitin is tough, damage is reduced by half."


class SpikedChitin(Evolution):
    name = "Spiked Chitin"
    cost = 10
    description = "Spikes now cover your body and enemies will hurt themselves with every attack"


class PoisonousHairs(Evolution):
    name = "Poisonous Hairs"
    cost = 20
    description = "Any creature stupid enough to attack you will fatally poison themselves."


class RazorPincers(Evolution):
    name = "Razor Pincers"
    cost = 5
    description = "Attacking a creature will also attack those adjacent to you and your target"


class BladedLegs(Evolution):
    name = "Bladed Legs"
    cost = 10
    description = "Every attack you make will also damage any adjacent creatures"


class HellishCharge(Evolution):
    name = "Hellish Charge"
    cost = 20
    description = "Charge in a direction, bringing death to any creature in your path."


class Abyssal(Evolution):
    name = "Abyssal Spider"
    cost = 1
    description = (
        "A spider brought from the deepest pits of a nameless abyss.\n"
        "It has the strength to overpower and consume all who opposes it.\n"
        "Luckily for the weak, it cannot reproduce without the hellish influences\n"
        "of the black pit, merely birthing vampiric abyssal flies.")


def abyssal_nodes():
    giant = EvolutionNode(evolution=Giant)
    devouring_maw = EvolutionNode(evolution=DevouringMaw, requires=[giant])
    swallow_whole = EvolutionNode(evolution=SwallowWhole, requires=[giant, devouring_maw])

    thick_chitin = EvolutionNode(evolution=ThickChitin)
    spiked_chitin = EvolutionNode(evolution=SpikedChitin, requires=[thick_chitin])
    poisonous_hairs = EvolutionNode(evolution=PoisonousHairs, requires=[thick_chitin, spiked_chitin])

    razor_pincers = EvolutionNode(evolution=RazorPincers)
    bladed_legs = EvolutionNode(evolution=BladedLegs, requires=[razor_pincers])
    hellish_charge = EvolutionNode(evolution=HellishCharge, requires=[razor_pincers, bladed_legs])

    abyssal = EvolutionNode(
        evolution=Abyssal,
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
