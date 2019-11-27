import random
import sys
import time

from bearlibterminal import terminal

from lotsqrl import movement, tiles, utils
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
    
    def act(self):
        host = self.host
        press = terminal.read()
        move_action = movement.move_actions.get(press)
        if move_action is not None:
            host.moved = move_action(host)

        if press == terminal.TK_E:
            host.moved = self.try_eat()
        elif press == terminal.TK_L:
            host.moved = self.lay_egg()
        elif press == terminal.TK_J:
            host.moved = self.jump()
        elif press == terminal.TK_KP_5:
            host.moved = True
        elif press == terminal.TK_F:
            host.moved = self.fire_web()
        elif press == terminal.TK_CLOSE:
            sys.exit()
        elif press == terminal.TK_F1:
            draw_help_file()
        elif press == terminal.TK_ESCAPE:
            if host.game.game_won:
                host.game.should_restart = True
                return
    
    def fire_web(self):
        # TODO THIS NEEDS TO BE ENTIRELY REWRITTEN
        host = self.host
        web_cooldown = host.cooldowns.get("web")
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
        
        # TODO This Needs to grab that Action Delay
        host.cooldowns.set("web", host.web_delay)

        for i in range(1, 10):
            web_x, web_y = host.x + (offset[0] * i), host.y + (offset[1] * i)
            if host.level.get_tile(web_x, web_y) == tiles.CaveWall:
                host.game.add_message("Your web hits a wall, press a key to fling yourhost.", show_now=True)
                offset = utils.get_directional_pos()
                if offset is None:
                    host.game.add_message("You snap your web with your fangs")
                    return True
                for wf in range(1, 5):
                    gx, gy = host.x + (offset[0] * wf), host.y + (offset[1] * wf)
                    actors = [actor for actor in host.level.get_actors_by_pos(gx, gy) if not actor.dead]
                    if actors:
                        actor = actors[0]
                        host.game.add_message("You smash against %s!" % actor.name)
                        actor.stunned = 2
                        host.x = gx - offset[0]
                        host.y = gy - offset[1]
                        host.hp -= random.randint(1, 4)
                        actor.hp -= random.randint(2, 8)
                        if host.hp < 0:
                            host.on_death()
                        if actor.hp < 0:
                            actor.on_death()
                        break
                    else:
                        tile = host.level.get_tile(gx, gy)
                        if tile == tiles.CaveWall:
                            host.x = gx - offset[0]
                            host.y = gy - offset[1]
                            break
                else:
                    host.x = gx
                    host.y = gy
                return True

            goblins = host.level.get_actors_by_pos(web_x, web_y, team=Team.Goblin)
            if goblins:
                goblin = goblins[0]
                if goblin is None:
                    continue
                host.game.add_message("You web latches on %s!" % goblin.name)
                host.game.add_message("Press direction to fling %s" % goblin.name, show_now=True)
                offset = utils.get_directional_pos()
                if offset is None:
                    host.game.add_message("You snap your web with your fangs")
                    return True
                host.game.add_message("You fling %s in the air!" % goblin.name)
                for wf in range(1, 5):
                    gx, gy = goblin.x + (offset[0] * wf), goblin.y + (offset[1] * wf)
                    actors = [actor for actor in host.level.get_actors_by_pos(gx, gy) if not actor.dead]
                    if actors:
                        actor = actors[0]
                        if actor == self and goblin != host.game.boss:
                            host.game.add_message("You catch %s and start spinning a cocoon!" % goblin.name)
                            goblin.dead = True
                            host.level.remove_actor(goblin)
                            # TODO This is BAD and will be swapped out
                            from lotsqrl.actors import Cocoon
                            new_cocoon = Cocoon(host.game, gx - offset[0], gy - offset[1])
                            host.level.add_actor(new_cocoon)
                            return True
                        host.game.add_message("%s smashes against %s!" % (goblin.name, actor.name))
                        goblin.stunned = 1
                        if actor != host.game.player:
                            actor.stunned = 1
                        goblin.x = gx - offset[0]
                        goblin.y = gy - offset[1]
                        goblin.hp -= random.randint(1, 4)
                        actor.hp -= random.randint(1, 4)
                        if goblin.hp < 0:
                            goblin.on_death()
                        if actor.hp < 0:
                            actor.on_death()
                        break
                    else:
                        tile = host.level.get_tile(gx, gy)
                        if tile == tiles.CaveWall:
                            host.game.add_message("%s smashes against the wall!" % goblin.name)
                            goblin.stunned = 3
                            goblin.hp -= random.randint(4, 8)
                            if goblin.hp < 0:
                                goblin.on_death()
                            goblin.x = gx - offset[0]
                            goblin.y = gy - offset[1]
                            break
                else:
                    goblin.x = gx
                    goblin.y = gy

                return True
            else:
                web_char = utils.direction_offsets_char.get(offset)
                graphics = host.game.options.graphical_tiles
                if graphics:
                    terminal.layer(2)
                # TODO Improve this way to draw something/animation now
                camera = host.game.camera
                camera.set_sprite_font()
                terminal.put(*camera.transform(web_x, web_y), web_char)
                camera.reset_font()
                if graphics:
                    terminal.layer(3)
                terminal.refresh()
                time.sleep(0.05)
        else:
            host.game.add_message("There is no one to web there.")

        return False

    def lay_egg(self):
        return self.host.actions.try_execute("lay_egg")

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

    def try_eat(self):
        host = self.host
        host.game.add_message("Press direction to eat corpse", show_now=True)
        offset = utils.get_directional_pos()
        if offset is None:
            host.game.add_message("Cancelled", show_now=True)
            return False

        tx, ty = host.x + offset[0], host.y + offset[1]
        targets = host.level.get_actors_by_pos(tx, ty, team=Team.Corpse)
        if targets:
            return host.actions.try_execute('eat_corpse', targets[0])

        host.game.add_message("No corpses there.", show_now=True)
        return False
