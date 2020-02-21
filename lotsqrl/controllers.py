import sys

from bearlibterminal import terminal

from lotsqrl import inputmap, movement
from lotsqrl.scenes.helpfile import draw_help_file
from lotsqrl.scenes.powers import PowersScene


class ActorController(object):
    def __init__(self, host):
        self.host = host
        
    def can_act(self):
        host = self.host
        if host.stunned > 0:
            host.stunned -= 1
            return False

        if host.dead or host.level is None:
            return False
        
        return True
        
    def act(self):
        pass
    

class NullController(ActorController):
    def can_act(self):
        return False


class AIController(ActorController):
    def act(self):
        host = self.host
        next_behavior = min(host.behaviors, key=lambda b: b.get_priority(host))
        return next_behavior.execute(host)


class PlayerController(ActorController):
    def __init__(self, host):
        super().__init__(host)
        self.actor_input_map = host.input_map()
        self.system_input_map = inputmap.SystemMapping()
    
    def act(self):
        host = self.host
        press = terminal.read()
        move_action = movement.move_actions.get(press)
        if move_action is not None:
            host.moved = move_action(host)
            if host.moved:
                return

        action_name = self.actor_input_map.get(press)
        if action_name is not None:
            host.moved = self.host.actions.try_execute(action_name)
        else:
            # TODO System actions must not be implemented here, only mapped
            system_input = self.system_input_map.get(press)
            if system_input == "exit_game":
                sys.exit()
            elif system_input == "open_manual":
                draw_help_file()
            elif system_input == "open_evolution":
                self.host.game.evolution_scene_active = True
            elif system_input == "open_powers":
                self.host.game.powers_scene = PowersScene(self.host)
                self.host.game.powers_selection_active = True
            elif system_input == "new_game":
                if host.game.game_won:
                    host.game.should_restart = True
                    return
