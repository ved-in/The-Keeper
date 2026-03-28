"""
ui/pause_menu.py — Pause menu overlay for The Keeper.

Draw on top of everything. ESC to toggle.
Buttons: Resume, Quit to Menu.
"""

import pygame
import core.view as view

# ── internal state ────────────────────────────────────────────────────────────
_active        = False
_font_title    = None
_font_btn      = None
_buttons: list[dict] = []        # list of {rect, label, action}
_hovered_index = -1

# ── colours ───────────────────────────────────────────────────────────────────
_OVERLAY_COLOUR  = (0,   0,   0,  160)   # semi-transparent black backdrop
_PANEL_COLOUR    = (15,  12,  10, 220)   # dark warm panel
_BORDER_COLOUR   = (120, 80,  40, 255)   # warm amber border
_TEXT_COLOUR     = (230, 210, 170)        # parchment
_HOVER_COLOUR    = (255, 220, 120)        # highlight
_BTN_COLOUR      = (30,  22,  15)        # button bg
_BTN_HOVER       = (55,  38,  20)        # button hover bg


def init():
    """Call once after pygame.font.init() — loads fonts."""
    global _font_title, _font_btn
    try:
        _font_title = pygame.font.Font("assets/fonts/IMFellEnglish-Regular.ttf", 42)
        _font_btn   = pygame.font.Font("assets/fonts/IMFellEnglish-Regular.ttf", 28)
    except (FileNotFoundError, pygame.error):
        _font_title = pygame.font.SysFont("serif", 42)
        _font_btn   = pygame.font.SysFont("serif", 28)


def toggle():
    global _active
    _active = not _active


def is_active() -> bool:
    return _active


def close():
    global _active
    _active = False


def handle_event(event, on_quit_to_menu) -> bool:
    """
    Returns True if the event was consumed by the pause menu.
    on_quit_to_menu: callable — called when the player chooses Quit to Menu.
    """
    global _active, _hovered_index

    if not _active:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            _active = True
            return True
        return False

    # ESC closes the menu
    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        _active = False
        return True

    if event.type == pygame.MOUSEMOTION:
        _hovered_index = _hit_button(event.pos)
        return True

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        idx = _hit_button(event.pos)
        if idx == 0:            # Resume
            _active = False
        elif idx == 1:          # Quit to Menu
            _active = False
            on_quit_to_menu()
        return True

    # swallow everything while paused
    return True


def draw(screen: pygame.Surface):
    if not _active:
        return

    sw, sh = screen.get_size()

    # ── dim backdrop ──────────────────────────────────────────────────────────
    backdrop = pygame.Surface((sw, sh), pygame.SRCALPHA)
    backdrop.fill(_OVERLAY_COLOUR)
    screen.blit(backdrop, (0, 0))

    # ── panel ─────────────────────────────────────────────────────────────────
    panel_w, panel_h = 340, 260
    panel_x = (sw - panel_w) // 2
    panel_y = (sh - panel_h) // 2

    panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    panel.fill(_PANEL_COLOUR)
    screen.blit(panel, (panel_x, panel_y))

    # border
    pygame.draw.rect(screen, _BORDER_COLOUR,
                     (panel_x, panel_y, panel_w, panel_h), 2, border_radius=4)

    # ── title ─────────────────────────────────────────────────────────────────
    if _font_title:
        title_surf = _font_title.render("Paused", True, _TEXT_COLOUR)
        title_rect = title_surf.get_rect(centerx=sw // 2, top=panel_y + 22)
        screen.blit(title_surf, title_rect)

    # ── buttons ───────────────────────────────────────────────────────────────
    _buttons.clear()
    labels   = ["Resume", "Quit to Menu"]
    btn_w    = 220
    btn_h    = 44
    btn_x    = (sw - btn_w) // 2
    start_y  = panel_y + 100

    for i, label in enumerate(labels):
        btn_y    = start_y + i * (btn_h + 16)
        btn_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        _buttons.append({"rect": btn_rect, "label": label})

        is_hovered = (i == _hovered_index)
        bg = _BTN_HOVER if is_hovered else _BTN_COLOUR
        tc = _HOVER_COLOUR if is_hovered else _TEXT_COLOUR

        pygame.draw.rect(screen, bg,           btn_rect, border_radius=3)
        pygame.draw.rect(screen, _BORDER_COLOUR, btn_rect, 1, border_radius=3)

        if _font_btn:
            text = _font_btn.render(label, True, tc)
            screen.blit(text, text.get_rect(center=btn_rect.center))


# ── helpers ───────────────────────────────────────────────────────────────────

def _hit_button(pos) -> int:
    for i, btn in enumerate(_buttons):
        if btn["rect"].collidepoint(pos):
            return i
    return -1