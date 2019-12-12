import sys

from bearlibterminal import terminal

from lotsqrl import inputmap, movement, tiles, utils
from lotsqrl.gameobjects import GridTarget
from lotsqrl.scenes.helpfile import draw_help_file
from lotsqrl.teams import Team


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
    # TODO This class will require using Input and Selectors
    # TODO The Input has to map actions
    # TODO The chosen action then needs a Selector
    # TODO This Selector can then be fed by using the behavior for NPCS
    # TODO but will have to bed fed manually by input for the player
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
            elif system_input == "new_game":
                if host.game.game_won:
                    host.game.should_restart = True
                    return


    def fire_web(self):
        # TODO This has been simplified
        # TODO It will need an Animator, Selector to properly behave
        host = self.host
        web_cooldown = host.cooldowns.get("spin_cocoon")
        if web_cooldown:
            host.game.add_message("You need to wait %s more rounds to fire web." % web_cooldown)
            return False

        host.game.add_message("Press direction to fire web", show_now=True)
        offset = utils.get_directional_pos()
        if offset is None:
            host.game.add_message("Cancelled", show_now=True)
            return False

        if host.score is not None:
            host.score.webs_fired += 1

        spin_cocoon_action = host.actions.get("spin_cocoon")
        web_range = spin_cocoon_action.reach
        max_web_x, max_web_y = host.x + (offset[0] * web_range), host.y + (offset[1] * web_range)
        target_line = utils.get_target_line(host, GridTarget(max_web_x, max_web_y))
        spin_cocoon_action.target_line = target_line
        obstacles = utils.get_obstacles_in_target_line(target_line)
        if not obstacles:
            host.game.add_message("There is no one to web there.")
            return False

        for obstacle in obstacles:
            if obstacle is tiles.CaveWall:
                host.game.add_message("Your web hits a wall.")
                # TODO This could allow the player to pull itself
                return True
            elif obstacle.team == Team.Goblin:
                host.cooldowns.set("web", spin_cocoon_action.cooldown)
                return spin_cocoon_action.execute(host, obstacle)

        return False

    def jump(self):
        host = self.host
        jump_cooldown = host.cooldowns.get("jump")
        if jump_cooldown:
            host.game.add_message("You need to wait %s more rounds to jump." % jump_cooldown)
            return False

        host.game.add_message("Press direction to jump", show_now=True)
        offset = utils.get_directional_pos()
        if offset is None:
            host.game.add_message("Cancelled", show_now=True)
            return False

        ox, oy = offset
        if ox != 0:
            ox *= 3
        if oy != 0:
            oy *= 3

        target = GridTarget(host.x + ox, host.y + oy)
        return host.actions.try_execute('jump', target)

