import pygame
import core.view as view

# registered minigame modules: { key: module }
_registry: dict = {}

_active_key: str | None = None
_slide_t: float = 0.0
_closing: bool = False
_done: bool = False

PANEL_HEIGHT = 320
SLIDE_SPEED = 3.5
CORNER_RADIUS = 14
HEADER_H = 28

COLORS = {
    "dim":     (0,   0,   0),
    "bg":      (14,  14,  24),
    "shadow":  (8,   8,   12),
    "border":  (96,  92,  116),
    "accent":  (172, 152, 108),
    "header":  (20,  20,  34),
    "title":   (210, 205, 190),
    "hint":    (120, 116, 134),
}


def register(key: str, module) -> None:
    _registry[key] = module


def open(key: str) -> None:
    global _active_key, _slide_t, _closing, _done
    if key not in _registry:
        return
    _active_key = key
    _closing = False
    _done = False
    if _slide_t <= 0.0:
        _slide_t = 0.0
    _registry[key].on_open()


def close() -> None:
    global _closing
    _closing = True


def is_open() -> bool:
    return _active_key is not None and (_slide_t > 0.0 or not _closing)


def is_blocking() -> bool:
    return _active_key is not None and _slide_t > 0.0


def handle_event(event: pygame.event.Event) -> bool:
    if not is_blocking():
        return False

    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        close()
        return True

    if _active_key:
        _registry[_active_key].handle_event(event)
    return True


def update(dt: float) -> None:
    global _slide_t, _active_key, _closing, _done
    
    if _active_key is None:
        return
    if _closing:
        _slide_t = max(0.0, _slide_t - SLIDE_SPEED * dt)
        if _slide_t <= 0.0:
            _active_key = None
            _closing = False
        return
        
    _slide_t = min(1.0, _slide_t + SLIDE_SPEED * dt)
    
    if _slide_t >= 1.0 and _active_key:
        _registry[_active_key].update(dt)
        if _done:
            close()


def notify_done() -> None:
    global _done
    _done = True


def reset_all() -> None:
    for module in _registry.values():
        if hasattr(module, "reset"):
            module.reset()


def draw(screen: pygame.Surface) -> None:
    if _active_key is None or _slide_t <= 0.0:
        return

    frame = view.content_rect()

    # --- eased slide position -------------------------------------------
    t = _ease_out(_slide_t)
    panel_h = view.scale(PANEL_HEIGHT)
    panel_y = frame.bottom - int(panel_h * t)

    panel_rect = pygame.Rect(frame.left, panel_y, frame.width, panel_h)

    # --- dim overlay behind panel ---------------------------------------
    dim_alpha = int(160 * t)
    dim = pygame.Surface((frame.width, frame.height), pygame.SRCALPHA)
    dim.fill((*COLORS["dim"], dim_alpha))
    screen.blit(dim, frame.topleft)

    # --- panel shadow ---------------------------------------------------
    shadow_rect = panel_rect.move(0, view.scale(5))
    pygame.draw.rect(screen, COLORS["shadow"], shadow_rect,
                     border_top_left_radius=view.scale(CORNER_RADIUS),
                     border_top_right_radius=view.scale(CORNER_RADIUS))

    # --- panel background -----------------------------------------------
    pygame.draw.rect(screen, COLORS["bg"], panel_rect,
                     border_top_left_radius=view.scale(CORNER_RADIUS),
                     border_top_right_radius=view.scale(CORNER_RADIUS))

    # --- accent line at top of panel ------------------------------------
    accent_rect = pygame.Rect(panel_rect.x, panel_rect.y,
                              panel_rect.width, view.scale(4))
    pygame.draw.rect(screen, COLORS["accent"], accent_rect,
                     border_top_left_radius=view.scale(CORNER_RADIUS),
                     border_top_right_radius=view.scale(CORNER_RADIUS))

    # --- border ---------------------------------------------------------
    pygame.draw.rect(screen, COLORS["border"], panel_rect,
                     width=max(1, view.scale(1)),
                     border_top_left_radius=view.scale(CORNER_RADIUS),
                     border_top_right_radius=view.scale(CORNER_RADIUS))

    # --- header bar with title + ESC hint -------------------------------
    header_rect = pygame.Rect(panel_rect.x,
                               panel_rect.y + view.scale(4),
                               panel_rect.width,
                               view.scale(HEADER_H))
    pygame.draw.rect(screen, COLORS["header"], header_rect)

    font_title = view.font(11, "assets/fonts/IMFellEnglish-Regular.ttf")
    font_hint  = view.font(8,  "assets/fonts/IMFellEnglish-Regular.ttf")

    title_text = _registry[_active_key].TITLE if _active_key else ""
    title_surf = font_title.render(title_text, True, COLORS["title"])
    screen.blit(title_surf, (
        header_rect.x + view.scale(16),
        header_rect.centery - title_surf.get_height() // 2,
    ))

    hint_surf = font_hint.render("ESC to close", True, COLORS["hint"])
    screen.blit(hint_surf, (
        header_rect.right - hint_surf.get_width() - view.scale(14),
        header_rect.centery - hint_surf.get_height() // 2,
    ))

    # --- content area handed to the minigame ----------------------------
    content_top = header_rect.bottom + view.scale(4)
    content_rect = pygame.Rect(panel_rect.x + view.scale(16),
                                content_top,
                                panel_rect.width - view.scale(32),
                                panel_rect.bottom - content_top - view.scale(12))
    
    # content was drawn before sliding
    # this will fix it
    if _slide_t >= 1.0 and _active_key:
        _registry[_active_key].draw(screen, content_rect)

def _ease_out(t: float) -> float:
    return 1.0 - (1.0 - t) ** 3