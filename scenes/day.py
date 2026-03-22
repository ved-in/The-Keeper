import pygame
import core.player as player
import ui.dialogue as dialogue
import ui.hud as hud
import scenes.lighthouse as lighthouse

import constants


def init():
    global _player
    _player = player.make_player()
    dialogue.clear()


# updates player position using player.update function
# the if block makes it so that player CANNOT move when dialogues are active
def update(dt):
    if not dialogue.active():
        player.update(_player, dt)


# handles events for the lighthouse game scene
# currently only has logic for advancing dialogues, but later will have more stuff for tasks and all
def handle_event(event):
    if event.type == pygame.KEYDOWN:
        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
            dialogue.advance()


def draw(screen):
    lighthouse.draw(screen)
    player.draw(screen, _player) # player rectangle
    dialogue.draw(screen) # dialogue box
    hud.draw(screen) # draws hud