import pygame
import core.player as player
import ui.dialogue as dialogue
import ui.hud as hud
import scenes.lighthouse as lighthouse
import constants
import core.view as view


def init():
    global _player
    _player = player.make_player()
    # reset the world scroll so every new day starts from the same position
    player.reset_world()
    dialogue.clear()


def update(dt):
    dialogue.update(dt)
    # block player movement while a dialogue box is showing
    if not dialogue.active():
        player.update(_player, dt)


def handle_event(event):
    if event.type == pygame.KEYDOWN and event.key in constants.ADVANCE_KEYS:
        dialogue.advance()


def draw(screen):
    lighthouse.draw(screen)
    player.draw(screen, _player)

def draw_ui(screen):
    dialogue.draw(screen, view.rect(_player["x"], _player["y"], _player["w"], _player["h"]))
    hud.draw(screen)
