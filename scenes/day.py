import pygame
import core.player as player
import ui.dialogue as dialogue
import ui.hud as hud
import scenes.lighthouse as lighthouse
import constants


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
    # draw the shared lighthouse background first, then the player on top
    lighthouse.draw(screen)
    # player.draw returns the screen rect of the player, needed to anchor the thought bubble
    player_rect = player.draw(screen, _player)
    dialogue.draw(screen, player_rect)
    hud.draw(screen)
