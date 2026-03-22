import pygame
import core.player as player
import ui.dialogue as dialogue
import ui.hud as hud
import scenes.lighthouse as lighthouse
import constants


def init():
    global _player
    _player = player.make_player()
    player.reset_world()
    dialogue.clear()


def update(dt):
    dialogue.update(dt)
    if not dialogue.active():
        player.update(_player, dt)


def handle_event(event):
    if event.type == pygame.KEYDOWN and event.key in constants.ADVANCE_KEYS:
        dialogue.advance()


def draw(screen):
    lighthouse.draw(screen)
    player_rect = player.draw(screen, _player)
    dialogue.draw(screen, player_rect)
    hud.draw(screen)
