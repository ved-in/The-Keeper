"""
Cool Down Engine  Pressure Valves minigame.

Five pressure valves are shown, each with a pressure value. Click them in
ascending pressure order (lowest to highest) to safely vent the system.
Clicking the wrong one resets progress.
"""

import random
import pygame
import core.view as view
from systems.minigame import Minigame
import core.sound as sound


_NUM_VALVES = 5


class PressureValves(Minigame):
    TITLE = "Release Pressure Valves"
    def __init__(self) -> None:
        super().__init__()
        self._pressures:   list[int]   = []
        self._order:       list[int]   = []
        self._released:    list[bool]  = []
        self._next_idx:    int         = 0
        self._wrong_flash: float       = 0.0
        self._content_rect: pygame.Rect | None = None
    
    def reset(self) -> None:
        super().reset()
        self._pressures   = random.sample(range(1, 10), _NUM_VALVES)
        self._order       = sorted(range(_NUM_VALVES), key=lambda i: self._pressures[i])
        self._released    = [False] * _NUM_VALVES
        self._next_idx    = 0
        self._wrong_flash = 0.0
    
    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i in range(_NUM_VALVES):
                if self._released[i]:
                    continue
                r = self._valve_rect(i)
                if r and r.collidepoint(event.pos):
                    if self._order[self._next_idx] == i:
                        self._released[i] = True
                        self._next_idx += 1
                        sound.play_vent()
                    else:
                        self._released    = [False] * _NUM_VALVES
                        self._next_idx    = 0
                        self._wrong_flash = 1.0
                    break
    
    def update(self, dt: float) -> None:
        if self._wrong_flash > 0:
            self._wrong_flash = max(0.0, self._wrong_flash - dt * 3)
        if all(self._released):
            self.complete()
    
    def draw(self, screen: pygame.Surface, content_rect: pygame.Rect) -> None:
        self._content_rect = content_rect
        font = view.font(10, "assets/fonts/IMFellEnglish-Regular.ttf")

        for i in range(_NUM_VALVES):
            r = self._valve_rect(i)
            if r is None:
                continue

            released = self._released[i]
            pressure = self._pressures[i]

            if released:
                body_col = (50, 48, 58)
            elif self._wrong_flash > 0:
                # 155 cuz then max body_col = 255, 40, 40.
                flash_r  = int(155 * self._wrong_flash)
                body_col = (100 + flash_r, 40, 40)
            else:
                t = (pressure - 1) / 8
                body_col = (int(60 + 160 * t), int(160 - 120 * t), 60)
                
            pygame.draw.rect(screen, body_col, r, border_radius=view.scale(6))
            pygame.draw.rect(screen, (100, 96, 116), r, width=max(1, view.scale(1)), border_radius=view.scale(6))

            if not released:
                bar_w = int((r.width - view.scale(8)) * (pressure / 9))
                bar_h = view.scale(6)
                bar_r = pygame.Rect(r.left + view.scale(4), r.bottom - bar_h - view.scale(4), bar_w, bar_h)
                pygame.draw.rect(screen, (230, 210, 100), bar_r, border_radius=view.scale(2))
                
            p_lbl = font.render(
                str(pressure) if not released else "✓",
                True,
                (240, 235, 210) if not released else (120, 200, 120),
            )
            screen.blit(p_lbl, (r.centerx - p_lbl.get_width() // 2, r.top + view.scale(6)))
            
            v_lbl = font.render("VENT", True, (150, 146, 164) if not released else (80, 80, 90))
            screen.blit(v_lbl, (r.centerx - v_lbl.get_width() // 2, r.bottom + view.scale(3)))
            
        if all(self._released):
            hint_text, hint_col = "Pressure vented. Engine cooling.", (172, 200, 150)
        elif self._wrong_flash > 0:
            hint_text, hint_col = "Wrong order! Starting over.", (210, 100, 100)
        else:
            remaining = _NUM_VALVES - self._next_idx
            hint_text, hint_col = f"Click valves lowest to highest. {remaining} left.", (150, 146, 164)
        self.draw_hint(screen, content_rect, hint_text, hint_col)
    
    def _valve_rect(self, idx: int) -> pygame.Rect | None:
        cr = self._content_rect
        if cr is None:
            return None
        vw     = view.scale(38)
        vh     = view.scale(52)
        total  = _NUM_VALVES * vw + (_NUM_VALVES - 1) * view.scale(12)
        start_x = cr.centerx - total // 2
        x = start_x + idx * (vw + view.scale(12))
        y = cr.centery - vh // 2 - view.scale(8)
        return pygame.Rect(x, y, vw, vh)


instance = PressureValves()
