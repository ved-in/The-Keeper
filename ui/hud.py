import math
import pygame
import constants
import core.day_cycle as day_cycle
import systems.tasks as tasks
import core.view as view


def draw(screen):
    # show the current day number and the time-of-day progress bar
    _draw_label(screen, f"Day {day_cycle.day}", (200, 195, 215))
    _draw_progress_bar(screen)
    task_list = tasks.get_day_tasks(day_cycle.day)
    done_list = [tasks.day_task_done(i) for i in range(len(task_list))]
    _draw_task_panel(screen, task_list, done_list)


def draw_night(screen, night_timer: float, night_duration: float, active_emergency: dict | None):
    _draw_label(screen, f"Night {day_cycle.day}", (120, 110, 150))
    _draw_night_task_panel(screen, night_timer, night_duration, active_emergency)

def _draw_label(screen, text, color):
    font = view.font(13, constants.FONT_PATH)
    lbl  = font.render(text, True, color)
    screen.blit(lbl, view.point(16, 16))


def _draw_progress_bar(screen):
    border = view.rect(16, 34, 132, 8)
    radius = max(1, view.scale(3))
    inner  = border.inflate(-view.scale(2), -view.scale(2))
    pygame.draw.rect(screen, (28, 26, 38), border, border_radius=radius)
    pygame.draw.rect(screen, (82, 76, 94), border, width=max(1, view.scale(1)), border_radius=radius)
    pygame.draw.rect(screen, (46, 54, 80), inner, border_radius=radius)
    fill = inner.copy()
    fill.width = int(inner.width * day_cycle.progress())
    if fill.width:
        pygame.draw.rect(screen, (180, 166, 124), fill, border_radius=radius)

def _draw_night_timer(screen, night_timer: float, night_duration: float, paused: bool):
    border = view.rect(16, 34, 132, 8)
    radius = max(1, view.scale(3))
    inner  = border.inflate(-view.scale(2), -view.scale(2))

    pygame.draw.rect(screen, (28, 26, 38), border, border_radius=radius)
    pygame.draw.rect(screen, (82, 76, 94),  border, width=max(1, view.scale(1)), border_radius=radius)
    pygame.draw.rect(screen, (46, 54, 80),  inner, border_radius=radius)

    progress = min(night_timer / max(night_duration, 0.001), 1.0)
    fill = inner.copy()
    fill.width = int(inner.width * progress)
    if fill.width:
        if paused:
            pulse = (math.sin(pygame.time.get_ticks() * 0.006) + 1.0) * 0.5
            bar_col = (int(180 + 40 * pulse), int(60 * pulse), 40)
        else:
            bar_col = (80, 140, 200)
        pygame.draw.rect(screen, bar_col, fill, border_radius=radius)

    font = view.font(8, constants.FONT_PATH)
    remaining = max(0.0, night_duration - night_timer)
    lbl_text  = "PAUSED" if paused else f"{int(remaining)}s"
    lbl_col   = (210, 80, 80) if paused else (120, 116, 140)
    lbl = font.render(lbl_text, True, lbl_col)
    screen.blit(lbl, (border.right + view.scale(4),
                       border.centery - lbl.get_height() // 2))


# NEED TO MOVE THESE TO CONSTANTS

_PANEL_X = 16
_PANEL_TOP = 48
_PANEL_W = 190
_ROW_H = 18
_PAD_X = 10
_PAD_TOP = 26
_PAD_BOT = 8
_HEADER_H = 16

_COL_BG = (20,  18,  30,  200)
_COL_BORDER = (60,  56,  80,  255)
_COL_HEADER = (255, 255, 255)
_COL_PENDING = (200, 195, 215)
_COL_DONE = (100, 210, 120)
_COL_STRIKE = (100, 210, 120)
_COL_EMERG = (220, 80,  80)
_COL_EMERG_BG = (60,  20,  20,  180)
_COL_BAR_BG = (40,  36,  56)
_COL_BAR_FILL = (100, 210, 120)
_COL_BOX = (60,  56,  80)
_COL_CHECK = (100, 210, 120)


def _draw_night_task_panel(screen, night_timer: float, night_duration: float, active_emergency: dict | None):
    font_hdr  = view.font(10, constants.FONT_PATH)
    font_task = view.font(9,  constants.FONT_PATH)
    
    main_done = night_timer >= night_duration and active_emergency is None
    
    num_rows  = 2 if active_emergency else 1
    panel_h   = _PAD_TOP + num_rows * _ROW_H + _PAD_BOT
    panel     = view.rect(_PANEL_X, _PANEL_TOP, _PANEL_W, panel_h)
    
    surf = pygame.Surface((panel.width, panel.height), pygame.SRCALPHA)
    pygame.draw.rect(surf, _COL_BG, pygame.Rect(0, 0, panel.width, panel.height), border_radius=view.scale(5))
    pygame.draw.rect(surf, _COL_BORDER, pygame.Rect(0, 0, panel.width, panel.height), width=max(1, view.scale(1)), border_radius=view.scale(5))
    screen.blit(surf, panel.topleft)
    
    # header
    hdr = font_hdr.render("TASKS", True, _COL_HEADER)
    screen.blit(hdr, (panel.left + view.scale(_PAD_X), panel.top  + view.scale(5)))
    
    # completion bar (fills when main task done)
    bar_y = panel.top + view.scale(_HEADER_H) + view.scale(4)
    bar_x = panel.left + view.scale(_PAD_X)
    bar_w = panel.width - view.scale(_PAD_X * 2)
    bar_h = view.scale(4)
    pygame.draw.rect(screen, _COL_BAR_BG, pygame.Rect(bar_x, bar_y, bar_w, bar_h), border_radius=view.scale(2))
    if main_done:
        pygame.draw.rect(screen, _COL_BAR_FILL, pygame.Rect(bar_x, bar_y, bar_w, bar_h), border_radius=view.scale(2))
    
    _draw_row(screen, font_task, panel, 0, "Ensure lighthouse operation", done=main_done, emergency=False)
    
    # --- row 1: emergency (if active) ---
    if active_emergency:
        em_name = f"EMERGENCY: {active_emergency['name']}"
        _draw_row(screen, font_task, panel, 1, em_name, done=False, emergency=True)


def _draw_row(screen, font, panel, row_idx: int, text: str, done: bool, emergency: bool):
    row_y  = panel.top + view.scale(_PAD_TOP) + row_idx * view.scale(_ROW_H)
    box_x  = panel.left + view.scale(_PAD_X)
    box_sz = view.scale(9)
    box    = pygame.Rect(box_x, row_y + (view.scale(_ROW_H) - box_sz) // 2, box_sz, box_sz)
    
    if emergency:
        # red pulsing background strip for the emergency row
        # X3r0Day's lighttower beam code really helped
        pulse = (math.sin(pygame.time.get_ticks() * 0.006) + 1.0) * 0.5
        strip_h = view.scale(_ROW_H)
        strip = pygame.Surface((panel.width, strip_h), pygame.SRCALPHA)
        alpha = int(80 + 60 * pulse)
        strip.fill((180, 30, 30, alpha))
        screen.blit(strip, (panel.left, row_y))
    
    box_col = (80, 20, 20) if emergency else _COL_BOX
    pygame.draw.rect(screen, box_col, box, border_radius=view.scale(2))
    if done:
        tx = box.left + view.scale(1)
        ty = box.top  + view.scale(1)
        bx = box.right  - view.scale(1)
        midx = box.left + box_sz // 3
        midy = box.bottom - view.scale(2)
        pygame.draw.lines(screen, _COL_CHECK, False,
                           [(tx + view.scale(1), ty + box_sz // 2),
                            (midx, midy), (bx, ty)],
                            max(1, view.scale(1)))
    else:
        border_col = (200, 60, 60) if emergency else (100, 96, 116)
        pygame.draw.rect(screen, border_col, box,
                        width=max(1, view.scale(1)),
                        border_radius=view.scale(2))
    
    text_col = _COL_EMERG if emergency else (_COL_DONE if done else _COL_PENDING)
    lbl      = font.render(text, True, text_col)
    text_x   = box.right + view.scale(6)
    text_y   = row_y + (view.scale(_ROW_H) - lbl.get_height()) // 2
    screen.blit(lbl, (text_x, text_y))
    
    if done and not emergency:
        strike_y = text_y + lbl.get_height() // 2
        pygame.draw.line(screen, _COL_STRIKE,
                          (text_x, strike_y),
                          (text_x + lbl.get_width(), strike_y),
                          max(1, view.scale(1)))

def _draw_task_panel(screen, task_list, done_list):
    if not task_list:
        return
    
    font_hdr  = view.font(10, constants.FONT_PATH)
    font_task = view.font(9,  constants.FONT_PATH)
    
    num_tasks = len(task_list)
    panel_h   = _PAD_TOP + num_tasks * _ROW_H + _PAD_BOT
    panel     = view.rect(_PANEL_X, _PANEL_TOP, _PANEL_W, panel_h)
    
    surf = pygame.Surface((panel.width, panel.height), pygame.SRCALPHA)
    pygame.draw.rect(surf, _COL_BG,
                     pygame.Rect(0, 0, panel.width, panel.height),
                     border_radius=view.scale(5))
    pygame.draw.rect(surf, _COL_BORDER,
                     pygame.Rect(0, 0, panel.width, panel.height),
                     width=max(1, view.scale(1)), border_radius=view.scale(5))
    screen.blit(surf, panel.topleft)
    
    hdr = font_hdr.render("TASKS", True, _COL_HEADER)
    screen.blit(hdr, (panel.left + view.scale(_PAD_X),
                       panel.top  + view.scale(5)))
    
    bar_y = panel.top + view.scale(_HEADER_H) + view.scale(4)
    bar_x = panel.left + view.scale(_PAD_X)
    bar_w = panel.width - view.scale(_PAD_X * 2)
    bar_h = view.scale(4)
    pygame.draw.rect(screen, _COL_BAR_BG,
                     pygame.Rect(bar_x, bar_y, bar_w, bar_h),
                     border_radius=view.scale(2))
    num_done = sum(done_list)
    if num_done:
        fill_w = int(bar_w * num_done / num_tasks)
        pygame.draw.rect(screen, _COL_BAR_FILL,
                         pygame.Rect(bar_x, bar_y, fill_w, bar_h),
                         border_radius=view.scale(2))

    for i, (task, done) in enumerate(zip(task_list, done_list)):
        _draw_row(screen, font_task, panel, i,
                  _task_display_name(task), done=done, emergency=False)


_DISPLAY_NAMES = {
    "Lens":        "Clean the Lens",
    "Logbook":     "Log Pressure",
    "Generator":   "Fix Wiring",
    "Breaker Box": "Flip Breakers",
    "Engine":      "Vent Engine",
    "Light Motor": "Crank the Light",
}


def _task_display_name(task: dict) -> str:
    key = task.get("interactable", "")
    return _DISPLAY_NAMES.get(key, key or "Unknown Task")