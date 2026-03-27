"""
Manual Light Crank minigame.

The motor is failing. Click the crank handle rapidly to keep the beam
spinning. Power drains over time and refills with each click. Sustain
power above zero for the full duration to complete the task.
"""

import math
import pygame
import core.view as view
from systems.minigame import Minigame

_DURATION      = 8.0
_DRAIN_RATE    = 0.18
_CLICK_POWER   = 0.22
_FAIL_RECOVERY = 0.4


class ManualCrank(Minigame):
    TITLE = "Manual Crank"
    def __init__(self) -> None:
        super().__init__()
        self._power:      float = 0.6
        self._elapsed:    float = 0.0
        self._angle:      float = 0.0
        self._fail_flash: float = 0.0
        self._complete:   bool  = False
        self._content_rect: pygame.Rect | None = None

    def reset(self) -> None:
        super().reset()
        self._power      = 0.6
        self._elapsed    = 0.0
        self._angle      = 0.0
        self._fail_flash = 0.0
        self._complete   = False
    
    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            handle = self._crank_handle_pos()
            if handle:
                hx, hy = handle
                mx, my = event.pos
                if math.hypot(mx - hx, my - hy) <= view.scale(18):
                    self._power  = min(1.0, self._power + _CLICK_POWER)
                    self._angle += 0.4

    def update(self, dt: float) -> None:
        if self._complete:
            return
        self._angle += dt * self._power * 2.5
        if self._power > 0:
            self._power   = max(0.0, self._power - _DRAIN_RATE * dt)
            self._elapsed = min(self._elapsed + dt, _DURATION)
        else:
            self._fail_flash = _FAIL_RECOVERY
            self._elapsed    = 0.0
            self._power      = 0.3
        if self._fail_flash > 0:
            self._fail_flash = max(0.0, self._fail_flash - dt)
        if self._elapsed >= _DURATION:
            self._complete = True
            self.complete()

    def draw(self, screen: pygame.Surface, content_rect: pygame.Rect) -> None:
        self._content_rect = content_rect
        font = view.font(10, "assets/fonts/IMFellEnglish-Regular.ttf")
        cx, cy = self._crank_center()

        # spinning beam
        beam_len = view.scale(60)
        bx = int(cx + math.cos(self._angle) * beam_len)
        by = int(cy + math.sin(self._angle) * beam_len)
        beam_surf = pygame.Surface((content_rect.width, content_rect.height), pygame.SRCALPHA)
        pygame.draw.line(
            beam_surf,
            (255, 240, 140, max(60, int(200 * self._power))),
            (cx - content_rect.left, cy - content_rect.top),
            (bx - content_rect.left, by - content_rect.top),
            max(2, view.scale(3)),
        )
        screen.blit(beam_surf, content_rect.topleft)

        # crank body
        radius = view.scale(28)
        body_col = (min(255, 80 + int(180 * self._fail_flash)), 40, 40) if self._fail_flash > 0 else (58, 54, 72)
        pygame.draw.circle(screen, body_col, (cx, cy), radius)
        pygame.draw.circle(screen, (100, 96, 116), (cx, cy), radius, max(1, view.scale(1)))

        # arm and handle
        arm_len = view.scale(22)
        ax = int(cx + math.cos(self._angle) * arm_len)
        ay = int(cy + math.sin(self._angle) * arm_len)
        pygame.draw.line(screen, (160, 150, 130), (cx, cy), (ax, ay), max(2, view.scale(3)))
        pygame.draw.circle(screen, (200, 180, 140), (ax, ay), view.scale(8))
        pygame.draw.circle(screen, (240, 235, 210), (ax, ay), view.scale(8), max(1, view.scale(1)))

        # power bar
        bar = self._power_bar_rect()
        if bar:
            pygame.draw.rect(screen, (28, 26, 38), bar, border_radius=view.scale(3))
            fill_w = int(bar.width * self._power)
            t = self._power
            bar_col = (int(200 * (1 - t)), int(60 + 140 * t), 60)
            if fill_w > 0:
                pygame.draw.rect(screen, bar_col, pygame.Rect(bar.left, bar.top, fill_w, bar.height), border_radius=view.scale(3))
            
            pygame.draw.rect(screen, (100, 96, 116), bar, width=max(1, view.scale(1)), border_radius=view.scale(3))
            pwr_lbl = font.render("POWER", True, (150, 146, 164))
            screen.blit(pwr_lbl, (bar.left, bar.top - pwr_lbl.get_height() - view.scale(2)))
        
        prog = self._progress_bar_rect()
        if prog:
            pygame.draw.rect(screen, (28, 26, 38), prog, border_radius=view.scale(3))
            fill_w = int(prog.width * (self._elapsed / _DURATION))
            if fill_w > 0:
                pygame.draw.rect(screen, (172, 152, 108), pygame.Rect(prog.left, prog.top, fill_w, prog.height), border_radius=view.scale(3))
            pygame.draw.rect(screen, (100, 96, 116), prog, width=max(1, view.scale(1)), border_radius=view.scale(3))
            pr_lbl = font.render("PROGRESS", True, (150, 146, 164))
            screen.blit(pr_lbl, (prog.left, prog.top - pr_lbl.get_height() - view.scale(2)))

        if self._complete:
            hint_text, hint_col = "The light holds!", (172, 200, 150)
        elif self._fail_flash > 0:
            hint_text, hint_col = "Power lost! Keep clicking!", (210, 100, 100)
        else:
            hint_text, hint_col = "Click the handle rapidly to keep the light spinning.", (150, 146, 164)
        self.draw_hint(screen, content_rect, hint_text, hint_col)

    def _crank_center(self) -> tuple[int, int]:
        cr = self._content_rect
        if cr is None:
            return (0, 0)
        return (cr.centerx, cr.top + int(cr.height * 0.42))

    def _crank_handle_pos(self) -> tuple[int, int] | None:
        cx, cy = self._crank_center()
        arm_len = view.scale(22)
        return (int(cx + math.cos(self._angle) * arm_len),
                int(cy + math.sin(self._angle) * arm_len))
    
    def _power_bar_rect(self) -> pygame.Rect | None:
        cr = self._content_rect
        if cr is None:
            return None
        bw = int(cr.width * 0.55)
        bx = cr.centerx - bw // 2
        by = cr.top + int(cr.height * 0.72)
        return pygame.Rect(bx, by, bw, view.scale(10))
    
    def _progress_bar_rect(self) -> pygame.Rect | None:
        cr = self._content_rect
        if cr is None:
            return None
        bw = int(cr.width * 0.55)
        bx = cr.centerx - bw // 2
        by = cr.top + int(cr.height * 0.72) + view.scale(22)
        return pygame.Rect(bx, by, bw, view.scale(10))


instance = ManualCrank()
