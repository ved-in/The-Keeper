import math
import pygame
import core.day_cycle as day_cycle
import core.player as player
import scenes.lighthouse as lighthouse
import constants
import ui.dialogue as dialogue
import ui.hud as hud

done = False
_player = player.make_player()
_t = 0.0


def init():
    global done, _player, _t
    done = False
    _player = player.make_player()
    _t = 0.0
    dialogue.show(constants.SCRIPTS.get(day_cycle.day, constants.FALLBACK_NIGHT_SCRIPT), style="thought")


def handle_event(event):
    global done
    if event.type == pygame.KEYDOWN and event.key in constants.ADVANCE_KEYS:
        if not dialogue.advance():
            done = True


def update(dt):
    global _t
    _t += dt
    dialogue.update(dt)
    if not dialogue.active():
        player.update(_player, dt)


def draw(screen):
    screen.fill(constants.SKY_COLORS["night"])
    lighthouse.draw(screen)

    pulse = (math.sin(_t * 3.2) + 1.0) * 0.5
    lighthouse.draw_beacon(
        screen,
        pulse=pulse,
        glow_radius=58,
        glow_pulse=18,
        glow_alpha=18,
        glow_alpha_pulse=14,
        inner_glow_radius=42,
        inner_glow_alpha=34,
        inner_glow_alpha_pulse=26,
        core_radius=40,
    )

    hud.draw_night(screen)
    player_rect = player.draw(screen, _player)
    dialogue.draw(screen, player_rect)
