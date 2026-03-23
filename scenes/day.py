import pygame
import core.player as player
import ui.dialogue as dialogue
import ui.hud as hud
import scenes.lighthouse as lighthouse
import constants
import core.view as view
import core.day_cycle as day_cycle

from core.interactables import Interactable
from core.visitors import Visitor

_interactables = []
_visitors = []

def init():
    global _player
    global _interactables, _visitors
    global _font
    _player = player.make_player()
    # reset the world scroll so every new day starts from the same position
    player.reset_world()
    dialogue.clear()
    
    _font = view.font(11)
    
    _interactables = [
        Interactable(
            o["name"],
            o["world_x"], o["y"],
            o["w"], o["h"], o["lines"], anim_path=o.get("anim_path"), anim_scale=o.get("anim_scale", 1.0))
        for o in constants.INTERACTABLES
    ]
    _visitors = [
        Visitor(
            v["name"],
            v["world_x"], v["y"],
            v.get("x_offset", 0), v.get("y_offset", 0),
            v["lines"],
            anim_folder=v.get("anim_folder"), anim_scale=v.get("anim_scale", 1.0)
        )
        for v in constants.VISITORS
    ]
    print("day init called")



def update(dt):
    dialogue.update(dt)
    # block player movement while a dialogue box is showing
    if not dialogue.active():
        player.update(_player, dt)

def _active_visitors():
    return [v for v in _visitors if day_cycle.day in v.lines_by_day]

def handle_event(event):
    if event.type == pygame.KEYDOWN and event.key in constants.ADVANCE_KEYS:
        dialogue.advance()
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        for obj in _interactables + _active_visitors():
            if obj.handle_click(event.pos, player._world_offset, day_cycle.day):
                break


def draw(screen):
    lighthouse.draw(screen)
    for obj in _interactables + _active_visitors():
        obj.draw(screen, player._world_offset, _font)
        print(obj.name, obj.screen_rect(player._world_offset))
    player.draw(screen, _player)
    print("interactables:", len(_interactables), "visitors:", len(_active_visitors()))
    print("font:", _font)

def draw_ui(screen):
    dialogue.draw(screen, view.rect(_player["x"], _player["y"], _player["w"], _player["h"]))
    hud.draw(screen)
