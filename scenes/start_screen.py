import math
import pygame
import scenes.lighthouse as lighthouse
import constants
import core.view as view

done = False

_t          = 0.0
_fade_in    = 1.8 # LOWW TAPERR FADEE
_blink_t    = 0.0 # for subtitle blinky blink
_dismissed  = False
_dismiss_t  = 0.0
_DISMISS_FADE = 0.9

_BG         = constants.SKY_COLORS["night"] # (25, 20, 45)
_GOLD       = (200, 175, 110)
_GOLD_DIM   = (140, 120, 72)
_WHITE      = (230, 225, 210)
_MUTED      = (130, 122, 145)
_VEIL       = (10, 12, 20, 110)


def init():
    global done, _t, _blink_t, _dismissed, _dismiss_t
    done       = False
    _t         = 0.0
    _blink_t   = 0.0
    _dismissed = False
    _dismiss_t = 0.0


def handle_event(event):
    global _dismissed
    
    if _t < _fade_in:
        return
    if _dismissed:
        return
    if event.type == pygame.KEYDOWN:
        _dismissed = True
    if event.type == pygame.MOUSEBUTTONDOWN:
        _dismissed = True


def update(dt):
    global done, _t, _blink_t, _dismiss_t
    _t      += dt
    _blink_t += dt
    if _dismissed:
        _dismiss_t += dt
        if _dismiss_t >= _DISMISS_FADE:
            done = True


def draw(screen):
    w, h = screen.get_size()
    cx   = w // 2
    
    screen.fill(_BG)
    lighthouse.draw(screen)
    
    veil = pygame.Surface((w, h), pygame.SRCALPHA)
    veil.fill(_VEIL)
    screen.blit(veil, (0, 0))
    
    p = math.sin(_t * 1.4) * 0.5 + 0.5
    lighthouse.draw_beacon(
        screen, pulse=p,
        glow_radius=52, glow_pulse=14,
        glow_alpha=16, glow_alpha_pulse=36,
        core_radius=32, core_pulse=5,
    )
    
    bar_h = max(view.scale(22), int(h * 0.055))
    pygame.draw.rect(screen, (0, 0, 0), (0, 0, w, bar_h))
    pygame.draw.rect(screen, (0, 0, 0), (0, h - bar_h, w, bar_h))
    
    rect_surf = pygame.Surface((600, 350), pygame.SRCALPHA)
    pygame.draw.rect(rect_surf, (0, 0, 0, 200), rect_surf.get_rect(), border_radius=20)
    screen.blit(rect_surf, rect_surf.get_rect(center=(640, 380)))
    
    title_font = view.font(46, constants.FONT_PATH)
    title_surf = title_font.render("THE KEEPER", True, _WHITE)
    title_rect = title_surf.get_rect(center=(cx, int(h * 0.42)))
    
    shadow_surf = title_font.render("THE KEEPER", True, (0, 0, 0))
    screen.blit(shadow_surf, title_rect.move(view.scale(2), view.scale(3)))
    screen.blit(title_surf, title_rect)
    
    # thin gold outline
    # chef's kiss MWAHHH
    rule_y  = title_rect.bottom + view.scale(10)
    rule_w  = view.scale(180)
    rule_h  = max(1, view.scale(1))
    pygame.draw.rect(screen, _GOLD_DIM,
                     (cx - rule_w // 2, rule_y, rule_w, rule_h))
    
    sub_font = view.font(11, constants.FONT_PATH)
    sub_surf = sub_font.render("A lighthouse keeper's vigil", True, _MUTED)
    sub_rect = sub_surf.get_rect(center=(cx, rule_y + view.scale(16)))
    screen.blit(sub_surf, sub_rect)
    
    # b l i n k
    if _t >= _fade_in and not _dismissed:
        blink_alpha = int(140 + 115 * math.sin(_blink_t * 2.8))
        prompt_font = view.font(10, constants.FONT_PATH)
        prompt_surf = prompt_font.render("— PRESS ANY KEY TO BEGIN —", True, _GOLD)
        prompt_surf.set_alpha(blink_alpha)
        prompt_rect = prompt_surf.get_rect(center=(cx, int(h * 0.70)))
        screen.blit(prompt_surf, prompt_rect)
    
    fade_alpha = 0
    if _t < _fade_in:
        fade_alpha = int(255 * (1.0 - (_t / _fade_in)))
    elif _dismissed:
        fade_alpha = int(255 * min(1.0, _dismiss_t / _DISMISS_FADE))
    
    if fade_alpha > 0:
        fade = pygame.Surface((w, h))
        fade.fill((0, 0, 0))
        fade.set_alpha(fade_alpha)
        screen.blit(fade, (0, 0))


def draw_ui(screen):
    # no HUD on the start screen
    pass