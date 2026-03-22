import pygame
import core.player as player
import ui.dialogue as dialogue
import ui.hud as hud


#   {"x": <x_pos>, "y": <y_pos>, "label": <text_label for when close>},
INTERACTABLES = [
]

#   [<dialog1>, <dialog2>.... <dialogn>] must be string
# This is for interactibles. When we get close to interactibles, we can press E or X or something to interact with them
RESPONSES = [
]

GROUND_Y = 400


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
    pygame.draw.rect(screen, (55, 50, 70), pygame.Rect(0, GROUND_Y, 960, 140))
    pygame.draw.rect(screen, (200, 195, 185), pygame.Rect(430, 120, 100, GROUND_Y - 120))
    pygame.draw.rect(screen, (240, 220, 130), pygame.Rect(420, 100, 120, 40))
    player.draw(screen, _player) # player rectangle
    dialogue.draw(screen) # dialogue box
    hud.draw(screen) # draws hud