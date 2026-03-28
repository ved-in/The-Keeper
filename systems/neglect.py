import math

import pygame

import constants
import core.view as view

_value = 0.0
_failed = False
_failure_text = constants.NEGLECT_FAILURE_DEFAULT


def reset() -> None:
    global _value, _failed, _failure_text
    _value = 0.0
    _failed = False
    _failure_text = constants.NEGLECT_FAILURE_DEFAULT


def value() -> float:
    return _value


def maximum() -> float:
    return float(constants.NEGLECT_MAX)


def ratio() -> float:
    return min(1.0, _value / max(maximum(), 0.001))


def failed() -> bool:
    return _failed


def add(amount: float, reason: str | None = None) -> bool:
    global _value
    if amount <= 0 or _failed:
        return False
    _value = min(maximum(), _value + amount)
    if _value >= maximum():
        _trigger_failure(reason)
        return True
    return False


def relieve(amount: float) -> None:
    global _value
    if amount <= 0 or _failed:
        return
    _value = max(0.0, _value - amount)


def update(dt: float) -> None:
    _ = dt


def handle_event(event: pygame.event.Event) -> bool:
    if not _failed:
        return False

    if event.type == pygame.KEYDOWN and (
        event.key in constants.ADVANCE_KEYS or event.key == pygame.K_r
    ):
        import core.game as game

        game.restart()
        return True

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        if _retry_btn_rect().collidepoint(event.pos):
            import core.game as game

            game.restart()
        return True

    return True


def draw_overlay(screen: pygame.Surface) -> None:
    if not _failed:
        return

    cr = view.content_rect()
    dim = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    dim.fill((0, 0, 0, 185))
    screen.blit(dim, (0, 0))

    panel_w = min(view.scale(420), cr.width - view.scale(40))
    panel_h = min(view.scale(240), cr.height - view.scale(56))
    panel = pygame.Rect(
        cr.centerx - panel_w // 2,
        cr.centery - panel_h // 2,
        panel_w,
        panel_h,
    )

    surf = pygame.Surface((panel.width, panel.height), pygame.SRCALPHA)
    pygame.draw.rect(surf, (14, 12, 18, 238), surf.get_rect(), border_radius=view.scale(8))
    pygame.draw.rect(
        surf,
        (88, 66, 70),
        surf.get_rect(),
        width=max(1, view.scale(1)),
        border_radius=view.scale(8),
    )

    pulse = 0.5 + 0.5 * math.sin(pygame.time.get_ticks() * 0.008)
    accent_col = (185, 72 + int(28 * pulse), 68)
    pygame.draw.rect(
        surf,
        accent_col,
        pygame.Rect(0, 0, surf.get_width(), view.scale(5)),
        border_top_left_radius=view.scale(8),
        border_top_right_radius=view.scale(8),
    )
    screen.blit(surf, panel.topleft)

    font_title = view.font(20, constants.FONT_PATH)
    font_body = view.font(10, constants.FONT_PATH)
    font_hint = view.font(9, constants.FONT_PATH)

    title = font_title.render(constants.NEGLECT_FAILURE_TITLE, True, (230, 214, 194))
    screen.blit(title, (panel.centerx - title.get_width() // 2, panel.top + view.scale(20)))

    reason_width = panel.width - view.scale(44)
    lines = _wrap_text(_failure_text, font_body, reason_width)
    text_y = panel.top + view.scale(70)
    for line in lines:
        lbl = font_body.render(line, True, (198, 188, 192))
        screen.blit(lbl, (panel.centerx - lbl.get_width() // 2, text_y))
        text_y += lbl.get_height() + view.scale(4)

    bar_border = pygame.Rect(
        panel.left + view.scale(30),
        panel.top + panel.height - view.scale(82),
        panel.width - view.scale(60),
        view.scale(12),
    )
    bar_inner = bar_border.inflate(-view.scale(2), -view.scale(2))
    pygame.draw.rect(screen, (30, 24, 30), bar_border, border_radius=view.scale(4))
    pygame.draw.rect(
        screen,
        (86, 76, 88),
        bar_border,
        width=max(1, view.scale(1)),
        border_radius=view.scale(4),
    )
    pygame.draw.rect(screen, (192, 72, 66), bar_inner, border_radius=view.scale(4))

    status = font_hint.render("Neglect reached its limit.", True, (214, 126, 116))
    screen.blit(
        status,
        (panel.centerx - status.get_width() // 2, bar_border.top - status.get_height() - view.scale(6)),
    )

    btn = _retry_btn_rect()
    hovered = btn.collidepoint(pygame.mouse.get_pos())
    btn_col = (76, 92, 64) if hovered else (56, 70, 48)
    pygame.draw.rect(screen, btn_col, btn, border_radius=view.scale(6))
    pygame.draw.rect(
        screen,
        (126, 164, 110),
        btn,
        width=max(1, view.scale(1)),
        border_radius=view.scale(6),
    )
    btn_lbl = font_body.render("Try Again", True, (218, 232, 208))
    screen.blit(btn_lbl, (btn.centerx - btn_lbl.get_width() // 2, btn.centery - btn_lbl.get_height() // 2))

    hint = font_hint.render("Press R or click the button to restart.", True, (148, 146, 154))
    screen.blit(hint, (panel.centerx - hint.get_width() // 2, panel.bottom - view.scale(26)))


def _trigger_failure(reason: str | None) -> None:
    global _failed, _value, _failure_text
    _failed = True
    _value = maximum()
    _failure_text = reason or constants.NEGLECT_FAILURE_DEFAULT
    try:
        import systems.minigame_overlay as minigame_overlay

        minigame_overlay.close()
    except Exception:
        pass


def _retry_btn_rect() -> pygame.Rect:
    cr = view.content_rect()
    w, h = view.scale(132), view.scale(36)
    return pygame.Rect(cr.centerx - w // 2, cr.centery + view.scale(46), w, h)


def _wrap_text(text: str, font, max_w: int) -> list[str]:
    words = text.split()
    if not words:
        return [""]

    lines = [words[0]]
    for word in words[1:]:
        trial = f"{lines[-1]} {word}"
        if font.size(trial)[0] <= max_w:
            lines[-1] = trial
        else:
            lines.append(word)
    return lines
