"""
Beach scene.

Only active on days defined in constants.BEACH_DAYS (currently Day 5).
The scientist has crates that need to be placed at marked spots.
"""

import pygame
import core.view as view
import core.day_cycle as day_cycle
import ui.dialogue as dialogue
import ui.hud as hud
import systems.tasks as tasks
import constants

_CRATE_SPOTS = [
    {"x": 200, "y": 350, "w": 34, "h": 28},
    {"x": 420, "y": 360, "w": 34, "h": 28},
    {"x": 640, "y": 345, "w": 34, "h": 28},
    {"x": 780, "y": 358, "w": 34, "h": 28},
]

_SAND_COL   = (180, 160, 120)
_WATER_COL  = (50,  80, 120)
_SKY_COL    = (62,  75, 110)

_crates_placed: list[bool] = []
_carrying: bool = False
_font = None
_task_idx: int = 0  # index in DAY_TASKS for this beach task
_crates_day: int = -1  # which day _crates_placed was built for


def init() -> None:
    global _crates_placed, _carrying, _font, _task_idx, _crates_day
    _font = view.font(9, constants.FONT_PATH)
    _carrying = False
    # find the beach task idx from the day task list
    _task_idx = 0
    for t in tasks.get_day_tasks(day_cycle.day):
        if t.get("task_type") == "beach":
            _task_idx = t.get("idx", 0)
            break
    # Only reset crate progress when entering the beach for the first time on
    # this day. Re-entering (e.g. going back to the lighthouse and returning)
    # preserves whatever crates the player has already placed.
    if _crates_day != day_cycle.day:
        _crates_placed = [False] * len(_CRATE_SPOTS)
        _crates_day = day_cycle.day


def handle_event(event: pygame.event.Event) -> None:
    global _carrying
    
    if event.type == pygame.KEYDOWN and event.key in constants.ADVANCE_KEYS:
        dialogue.advance()
    
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        if not dialogue.active():
            _handle_click(event.pos)


def _handle_click(pos) -> None:
    global _carrying
    
    # pick up crates from scientist pile
    if not _carrying:
        pile = _crate_pile_rect()
        if pile.collidepoint(pos) and not all(_crates_placed):
            _carrying = True
            dialogue.show(["You pick up a sensor crate."], style="thought", default_speaker="player")
            return
    
    # place on a spot
    if _carrying:
        for i, spot in enumerate(_CRATE_SPOTS):
            if _crates_placed[i]:
                continue
            r = _spot_rect(spot)
            if r.collidepoint(pos):
                _crates_placed[i] = True
                _carrying = False
                dialogue.show(["Sensor placed."], style="thought", default_speaker="player")
                if all(_crates_placed):
                    import scenes.day as day_scene
                    day_scene.notify_task_done(_task_idx)
                    dialogue.show(["All sensors placed.", "The scientist gives a curt nod."],
                                  style="thought", default_speaker="player")
                return
    
    # talk to scientist
    sci = _scientist_rect()
    if sci.collidepoint(pos):
        lines = constants.VISITORS[0]["lines"].get(day_cycle.day,
               constants.VISITORS[0]["lines"].get("default", ["..."]))
        dialogue.show(lines, reveal_speed=40)
        return
    
    # back button
    if _back_rect().collidepoint(pos):
        import core.game as game
        game.switch("lighthouse")


def update(dt: float) -> None:
    dialogue.update(dt)


def draw(screen: pygame.Surface) -> None:
    cr = view.content_rect()
    
    # sky
    pygame.draw.rect(screen, _SKY_COL, cr)
    
    # water strip
    water = pygame.Rect(cr.left, cr.top + int(cr.height * 0.3), cr.width, int(cr.height * 0.25))
    pygame.draw.rect(screen, _WATER_COL, water)
    
    # sand
    sand = pygame.Rect(cr.left, water.bottom, cr.width, cr.height - water.height - int(cr.height * 0.3))
    pygame.draw.rect(screen, _SAND_COL, sand)
    
    # placement spots (marked X)
    for i, spot in enumerate(_CRATE_SPOTS):
        r = _spot_rect(spot)
        if _crates_placed[i]:
            pygame.draw.rect(screen, (80, 160, 90), r, border_radius=view.scale(3))
            lbl = _font.render("✓", True, (200, 240, 200))
            screen.blit(lbl, (r.centerx - lbl.get_width() // 2, r.centery - lbl.get_height() // 2))
        else:
            pygame.draw.rect(screen, (160, 140, 100), r, width=max(1, view.scale(2)), border_radius=view.scale(2))
            lbl = _font.render("X", True, (200, 180, 120))
            screen.blit(lbl, (r.centerx - lbl.get_width() // 2, r.centery - lbl.get_height() // 2))
    
    # crate pile at scientist
    if not all(_crates_placed):
        pile = _crate_pile_rect()
        pygame.draw.rect(screen, (140, 110, 70), pile, border_radius=view.scale(3))
        pygame.draw.rect(screen, (170, 140, 90), pile, width=max(1, view.scale(1)), border_radius=view.scale(3))
        lbl = _font.render("Crates", True, (240, 230, 200))
        screen.blit(lbl, (pile.centerx - lbl.get_width() // 2, pile.top - lbl.get_height() - view.scale(3)))
    
    # scientist
    sci = _scientist_rect()
    pygame.draw.rect(screen, (160, 140, 180), sci, border_radius=view.scale(3))
    lbl = _font.render("Scientist", True, (230, 220, 240))
    screen.blit(lbl, (sci.centerx - lbl.get_width() // 2, sci.top - lbl.get_height() - view.scale(3)))
    
    # carrying indicator
    if _carrying:
        mx, my = pygame.mouse.get_pos()
        cw, ch = view.scale(24), view.scale(18)
        carry_surf = pygame.Surface((cw, ch), pygame.SRCALPHA)
        carry_surf.fill((140, 110, 70, 210))
        screen.blit(carry_surf, (mx - cw // 2, my - ch // 2))


def draw_ui(screen: pygame.Surface) -> None:
    hud.draw(screen)
    _draw_back_button(screen)
    dialogue.draw(screen)
    if not dialogue.active() and not all(_crates_placed):
        if not _carrying:
            lines = [
                "Click the crate pile to pick up a sensor.",
                "Then place it on one of the marked X spots.",
            ]
        else:
            lines = [
                "You are carrying a sensor.",
                "Click one of the marked X spots to place it.",
            ]
        hud.draw_help_card(screen, "Beach Task", lines, accent=(120, 164, 214))


def _draw_back_button(screen: pygame.Surface) -> None:
    r = _back_rect()
    col = (50, 46, 66) if not r.collidepoint(pygame.mouse.get_pos()) else (70, 66, 90)
    pygame.draw.rect(screen, col, r, border_radius=view.scale(4))
    pygame.draw.rect(screen, (90, 86, 110), r, width=max(1, view.scale(1)), border_radius=view.scale(4))
    lbl = _font.render("← Back", True, (200, 195, 215))
    screen.blit(lbl, (r.centerx - lbl.get_width() // 2, r.centery - lbl.get_height() // 2))


def _back_rect() -> pygame.Rect:
    return view.rect(10, 490, 60, 22)


def _spot_rect(spot: dict) -> pygame.Rect:
    return view.rect(spot["x"], spot["y"], spot["w"], spot["h"])


def _crate_pile_rect() -> pygame.Rect:
    return view.rect(120, 340, 50, 36)


def _scientist_rect() -> pygame.Rect:
    return view.rect(80, 300, 28, 48)
