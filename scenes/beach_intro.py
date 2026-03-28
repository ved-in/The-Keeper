"""
Beach Intro scene — plays once before Day 1.

The player can walk freely across the beach (screen-bounded, no world scroll).
The fisherman stands on the dock as a Visitor. Click him to trigger day 1
dialogue. Once the last line is dismissed, done = True -> game switches to day 1.
"""

import pygame
import ui.dialogue as dialogue
import constants
import core.view as view
import entities.player as player
import entities.animations as animations
from entities.visitors import Visitor

done    = False
_player = None
_fisherman: Visitor | None = None
_font   = None

_LEFT_EDGE = 40
_RIGHT_EDGE = 920
_GROUND_Y = 360

# Beach/Sand color
_SAND_COLOR = (232, 210, 155)


def init():
    global done, _player, _fisherman, _font
    done = False
    
    _player = player.make_player()
    _player["x"] = 160.0
    _player["y"] = float(_GROUND_Y - _player["h"]) 
    
    player.reset_world()
    _font = view.font(11, constants.FONT_PATH)
    
    # fisherman setup
    _fisherman = Visitor(
        name="Fisherman",
        world_x=680,
        y=_GROUND_Y,
        y_offset=0,
        lines_by_day={1: constants.VISITORS[1]["lines"][1]},
        anim_key="fisherman",
        anim_scale=2.0,
    )

def handle_event(event):
    global done
    
    if event.type == pygame.KEYDOWN and event.key in constants.ADVANCE_KEYS:
        if dialogue.active():
            if not dialogue.advance():
                # last line dismissed — end the scene
                done = True
    
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        if not dialogue.active() and _fisherman:
            _fisherman.handle_click(event.pos, 0, 1)


def update(dt):
    dialogue.update(dt)
    
    if dialogue.active():
        # freeze player while dialogue is showing
        _player["moving"] = False
        return
    
    _update_player(dt)
    
    if _fisherman:
        _fisherman.update(pygame.mouse.get_pos(), 0)


def draw(screen):
    # Draw the sand ground so the player isn't walking on air
    w, h = screen.get_size()
    ground_y_px = view.scale(_GROUND_Y)
    pygame.draw.rect(screen, _SAND_COLOR, (0, ground_y_px, w, h - ground_y_px))

    # background is drawn by game.py via sky_color() — just draw scene elements
    _fisherman.draw(screen, 0, _font, flip=True)
    player.draw(screen, _player)
    
    dialogue.draw(
        screen,
        player_rect = view.rect(_player["x"], _player["y"], _player["w"], _player["h"]),
        npc_rect    = _fisherman.screen_rect(0) if _fisherman else None,
    )


def draw_ui(screen):
    pass


def _update_player(dt):
    keys = pygame.key.get_pressed()
    key_dir = (int(keys[pygame.K_LEFT]  or keys[pygame.K_a]) - int(keys[pygame.K_RIGHT] or keys[pygame.K_d]))

    # click-to-move: set target when clicking on the ground
    if pygame.mouse.get_pressed()[0] and not dialogue.active():
        raw_x = pygame.mouse.get_pos()[0]
        base_x = view.un_x(raw_x)
        
        if _fisherman and not _fisherman.screen_rect(0).collidepoint(pygame.mouse.get_pos()):
            _player["target_world_x"] = max(_LEFT_EDGE, min(base_x, _RIGHT_EDGE - _player["w"]))
    
    if key_dir != 0:
        _player["target_world_x"] = None   # keyboard overrides click target
    
    direction = 0
    if key_dir != 0:
        direction = key_dir
    elif _player.get("target_world_x") is not None:
        dist = _player["target_world_x"] - _player["x"]
        step = constants.SPEED * dt
        if abs(dist) <= step:
            _player["x"]              = _player["target_world_x"]
            _player["target_world_x"] = None
        else:
            direction = -1 if dist > 0 else 1
    
    # move player x directly, clamped to screen edges
    if direction:
        _player["x"] = max(
            float(_LEFT_EDGE),
            min(_player["x"] - direction * constants.SPEED * dt,
                float(_RIGHT_EDGE - _player["w"]))
        )
    
    new_state = "walk" if direction else "idle"
    if _player.get("anim_state") != new_state:
        _player["anim_state"] = new_state
        animations.reset("mc")
    
    _player["moving"]      = bool(direction)
    _player["facing_left"] = direction > 0 if direction else _player.get("facing_left", False)