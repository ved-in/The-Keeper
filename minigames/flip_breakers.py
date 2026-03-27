"""
Fix Main Breaker minigame.

A breaker panel shows N switches. Some are tripped RED. Click each red
switch to flip it back to GREEN. All green = done.
"""

import random
import pygame
import core.view as view
from systems.minigame import Minigame

_COLS        = 4
_ROWS        = 2
_NUM_TRIPPED = 5


class FlipBreakers(Minigame):
    TITLE = "Fix the Breaker"
    def __init__(self) -> None:
        super().__init__()
        self._switches: list[bool] = []
        self._flip_anim: list[float] = []
        self._content_rect: pygame.Rect | None = None
    
    def reset(self) -> None:
        super().reset()
        self._switches = [True] * (_COLS * _ROWS)
        self._flip_anim = [0.0] * (_COLS * _ROWS)
        for i in random.sample(range(_COLS * _ROWS), _NUM_TRIPPED):
            self._switches[i] = False
    
    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i in range(_COLS * _ROWS):
                if not self._switches[i]:
                    r = self._switch_rect(i)
                    if r and r.collidepoint(event.pos):
                        self._switches[i] = True
                        self._flip_anim[i] = 1.0
    
    def update(self, dt: float) -> None:
        for i in range(len(self._flip_anim)):
            if self._flip_anim[i] > 0:
                self._flip_anim[i] = max(0.0, self._flip_anim[i] - dt * 4)
        if all(self._switches):
            self.complete()
    
    def draw(self, screen: pygame.Surface, content_rect: pygame.Rect) -> None:
        self._content_rect = content_rect
        font     = view.font(9,  "assets/fonts/IMFellEnglish-Regular.ttf")
        font_big = view.font(11, "assets/fonts/IMFellEnglish-Regular.ttf")

        panel = self._panel_rect()
        if panel:
            pygame.draw.rect(screen, (28, 26, 38), panel, border_radius=view.scale(6))
            pygame.draw.rect(screen, (80, 76, 96), panel, width=max(1, view.scale(1)), border_radius=view.scale(6))
        
        for i in range(_COLS * _ROWS):
            r = self._switch_rect(i)
            if r is None:
                continue
            on    = self._switches[i]
            flash = self._flip_anim[i]
            body_color = (40, 160, 80) if on else (180, 50, 50)
            if flash > 0:
                body_color = tuple(min(255, int(c + 120 * flash)) for c in body_color)
            pygame.draw.rect(screen, body_color, r, border_radius=view.scale(4))
            pygame.draw.rect(screen, (200, 196, 216), r, width=max(1, view.scale(1)), border_radius=view.scale(4))
            nub_h = r.height // 3
            nub_w = r.width  - view.scale(6)
            nub_x = r.centerx - nub_w // 2
            nub_y = r.top + view.scale(3) if on else r.bottom - nub_h - view.scale(3)
            pygame.draw.rect(screen, (230, 225, 210), pygame.Rect(nub_x, nub_y, nub_w, nub_h), border_radius=view.scale(2))
            lbl = font.render("ON" if on else "OFF", True, (220, 240, 220) if on else (240, 180, 180))
            screen.blit(lbl, (r.centerx - lbl.get_width() // 2, r.bottom + view.scale(2)))
        
        remaining = self._switches.count(False)
        if remaining == 0:
            hint_text, hint_col = "All breakers restored!", (172, 200, 150)
        else:
            hint_text, hint_col = f"Flip the red switches. {remaining} remaining.", (150, 146, 164)
        self.draw_hint(screen, content_rect, hint_text, hint_col, font_size=11)

    def _panel_rect(self) -> pygame.Rect | None:
        cr = self._content_rect
        if cr is None:
            return None
        pw = int(cr.width  * 0.72)
        ph = int(cr.height * 0.70)
        return pygame.Rect(cr.centerx - pw // 2, cr.top + view.scale(6), pw, ph)

    def _switch_rect(self, idx: int) -> pygame.Rect | None:
        panel = self._panel_rect()
        if panel is None:
            return None
        col    = idx % _COLS
        row    = idx // _COLS
        pad_x  = view.scale(14)
        pad_y  = view.scale(12)
        cell_w = (panel.width  - pad_x * 2) // _COLS
        cell_h = (panel.height - pad_y * 2) // _ROWS
        sw = int(cell_w * 0.55)
        sh = int(cell_h * 0.70)
        x  = panel.left + pad_x + col * cell_w + (cell_w - sw) // 2
        y  = panel.top  + pad_y + row * cell_h + (cell_h - sh) // 2
        return pygame.Rect(x, y, sw, sh)


instance = FlipBreakers()