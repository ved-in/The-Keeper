import math
import pygame
import scenes.lighthouse as lighthouse
import ui.dialogue as dialogue
import constants
import core.view as view

# set to True when the player finishes reading, signals game.py to move to the day scene
done = False
_t = 0.0


def init():
    global done, _t
    done = False
    _t = 0.0
    log_ui = constants.LOG_DIALOGUE
    # show the opening narration in the wide log panel style
    dialogue.show(
        constants.OPENING_LINES,
        style="log",
        label=log_ui["label"],
        reveal_speed=log_ui["reveal_speed"],
        sound_path=constants.DEFAULT_TYPE_SOUND,
    )


def handle_event(event):
    global done
    if event.type == pygame.KEYDOWN and event.key in constants.ADVANCE_KEYS:
        if not dialogue.advance():
            done = True


def update(dt):
    global _t
    _t += dt
    lighthouse.update_clouds(dt, night=True)
    if not done:
        dialogue.update(dt)


def draw(screen):
    cfg = constants.OPENING_SCENE
    screen.fill(constants.SKY_COLORS["night"])
    lighthouse.draw(screen, night=True)
    w, h = screen.get_size()

    # semi-transparent dark overlay to give the opening a moody dim look
    veil = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    veil.fill(cfg["veil"])
    screen.blit(veil, (0, 0))

    # beacon pulse builds up and fades away between pulse_start and pulse_end seconds
    p = 0.0
    if cfg["pulse_start"] <= _t <= cfg["pulse_end"]:
        # sin over 0 to pi gives a smooth rise and fall
        p = math.sin(math.pi * ((_t - cfg["pulse_start"]) / (cfg["pulse_end"] - cfg["pulse_start"])))

    lighthouse.draw_beacon(
        screen,
        pulse=p,
        glow_radius=cfg["glow_radius"],
        glow_pulse=cfg["glow_pulse"],
        glow_alpha=cfg["glow_alpha"],
        glow_alpha_pulse=cfg["glow_alpha_pulse"],
        core_radius=cfg["beacon_radius"],
        core_pulse=cfg["beacon_pulse"],
    )

    # black bars at top and bottom for a cinematic letterbox look
    bar_h = max(view.scale(cfg["letterbox_h"]), int(h * cfg["letterbox_ratio"]))
    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(0, 0, w, bar_h))
    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(0, h - bar_h, w, bar_h))

    dialogue.draw(screen)

    # fade in from black at the very start of the opening
    if _t < cfg["fade_in"]:
        fade = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        fade.fill((0, 0, 0, int(255 * (1.0 - (_t / cfg["fade_in"])))))
        screen.blit(fade, (0, 0))