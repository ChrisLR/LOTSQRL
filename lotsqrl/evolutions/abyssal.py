from lotsqrl import actions, armors
from lotsqrl.evolutions.base import EvolutionNode, Evolution


class Giant(Evolution):
    name = "Giant"
    cost = 5
    description = (
        "Grow into a monstrous size.\n"
        "Doubles starting and max health")

    def on_apply(self):
        host = self.host
        self.host.health.max_hp *= 2
        self.host.health.hp *= 2
        host.game.messaging.add_scoped_message(
            message_actor=f"You rapidly grow into a monstrous size!",
            message_others=f"{host.name} rapidly grows into a monstrous size!",
            actor=host
        )

    def on_remove(self):
        host = self.host
        new_max = int(round(host.health.max_hp / 2))
        host.health.max_hp = new_max
        if host.health.hp > new_max:
            host.health.hp = new_max

        host.game.messaging.add_scoped_message(
            message_actor=f"You rapidly shrink into your normal size!",
            message_others=f"{host.name} rapidly shrinks into its regular size!",
            actor=host
        )


class DevouringMaw(Evolution):
    name = "Devouring Maw"
    cost = 10
    description = "Killing an enemy consumes it instantly"

    def __init__(self, host):
        super().__init__(host)
        self._old_action = None

    def on_apply(self):
        host = self.host
        host.game.messaging.add_scoped_message(
            message_actor=f"Your jaws enlarge to a disproportionate size!",
            message_others=f"{host.name}'s jaws enlarge to a disproportionate size!",
            actor=host
        )
        # TODO Replacing an action is not a good idea
        # TODO Should simply be a new action and we change the Bump Action
        self._old_action = host.actions.get("bite")
        host.actions.actions["bite"] = actions.DevouringMaw(self._old_action.damage, self._old_action.reach)

    def on_remove(self):
        host = self.host
        host.game.messaging.add_scoped_message(
            message_actor=f"Your jaws shrink to a relatively normal size.",
            message_others=f"{host.name}'s jaws shrink to a relatively normal size.",
            actor=host
        )
        host.actions.actions["bite"] = self._old_action


class SwallowWhole(Evolution):
    name = "Swallow Whole"
    cost = 20
    description = "Swallow a live enemy, regenerating as you digest it"

    def on_apply(self):
        host = self.host
        host.game.messaging.add_scoped_message(
            message_actor=f"You are now able to digest live squirming victims.",
            actor=host
        )
        # TODO Not a good way to add powers
        swallow_whole = actions.SwallowWhole()
        host.actions.actions["swallow_whole"] = swallow_whole
        host.actions.powers["swallow_whole"] = swallow_whole

    def on_remove(self):
        host = self.host
        host.game.messaging.add_scoped_message(
            message_actor=f"You are no longer able to digest live squirming victims.",
            actor=host
        )
        del host.actions.actions["swallow_whole"]


class ThickChitin(Evolution):
    name = "Thick Chitin"
    cost = 5
    description = "Your chitin is tough, damage is reduced by half."

    def on_apply(self):
        self.host.armor.set(armors.ThickChitin)

    def on_remove(self):
        # TODO This should just remove the specific armor and will break out if ever removed right now
        self.host.armor.set(None)


class SpikedChitin(Evolution):
    name = "Spiked Chitin"
    cost = 10
    description = "Spikes now cover your body and enemies will hurt themselves with every attack"

    def on_apply(self):
        self.host.armor.set(armors.SpikedChitin)

    def on_remove(self):
        # TODO This should just remove the specific armor and will break out if ever removed right now
        self.host.armor.set(None)


class PoisonousHairs(Evolution):
    name = "Poisonous Hairs"
    cost = 20
    description = "Any creature stupid enough to attack you will fatally poison themselves."

    def on_apply(self):
        self.host.armor.set(armors.PoisonousHairs)

    def on_remove(self):
        # TODO This should just remove the specific armor and will break out if ever removed right now
        self.host.armor.set(None)


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
