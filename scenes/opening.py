import math
import pygame
import scenes.lighthouse as lighthouse
import ui.dialogue as dialogue
import constants
import core.view as view

done = False
_t = 0.0


def init():
    global done, _t
    log_ui = constants.LOG_DIALOGUE
    done = False
    _t = 0.0
    # load opening narration into the shared dialogue ui
    dialogue.show(
        constants.OPENING_LINES,
        style="log",
        label=log_ui["label"],
        reveal_speed=log_ui["reveal_speed"],
        sound_path=constants.DEFAULT_TYPE_SOUND,
    )


def handle_event(event):
    global done
    if event.type == pygame.KEYDOWN:
        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
            if not dialogue.advance():
                done = True


def update(dt):
    global _t
    _t += dt
    if not done:
        dialogue.update(dt)


def draw(screen):
    cfg = constants.OPENING_SCENE
    screen.fill(constants.SKY_COLORS["night"])
    lighthouse.draw(screen)
    w, h = screen.get_size()
    cx = view.x(480)
    cy = view.y(200)

    # dim veil
    veil = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    veil.fill(cfg["veil"])
    screen.blit(veil, (0, 0))

    # beacon pulse
    p = 0.0
    if cfg["pulse_start"] <= _t <= cfg["pulse_end"]:
        phase = (_t - cfg["pulse_start"]) / (cfg["pulse_end"] - cfg["pulse_start"])
        p = math.sin(math.pi * phase)

    gr = view.scale(cfg["glow_radius"] + int(cfg["glow_pulse"] * p))
    glow = pygame.Surface((gr * 2, gr * 2), pygame.SRCALPHA)
    pygame.draw.circle(
        glow,
        (255, 230, 120, cfg["glow_alpha"] + int(cfg["glow_alpha_pulse"] * p)),
        (gr, gr),
        gr,
    )
    screen.blit(glow, (cx - gr, cy - gr))
    pygame.draw.circle(screen, (255, 230, 120), (cx, cy), view.scale(cfg["beacon_radius"] + int(cfg["beacon_pulse"] * p)))

    # letterbox bars
    bar_h = max(view.scale(cfg["letterbox_h"]), int(h * cfg["letterbox_ratio"]))
    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(0, 0, w, bar_h))
    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(0, h - bar_h, w, bar_h))

    dialogue.draw(screen)

    # fade in
    if _t < cfg["fade_in"]:
        fade = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        fade.fill((0, 0, 0, int(255 * (1.0 - (_t / cfg["fade_in"])))))
        screen.blit(fade, (0, 0))
