"""
Lubricate Engine minigame.

Four engine ports are shown. The player clicks and drags a nozzle
over each port to lubricate it. All four done = complete.
"""

import pygame
import core.view as view
from systems.minigame import Minigame

_NUM_PORTS = 4
_NOZZLE_RADIUS = 14  # base units


class LubricateEngine(Minigame):
    TITLE = "Lubricate Engine"
    def __init__(self) -> None:
        super().__init__()
        self._lubed: list[bool] = []
        self._dragging: bool = False
        self._has_can: bool = False
        self._content_rect: pygame.Rect | None = None
    
    def reset(self) -> None:
        super().reset()
        self._lubed = [False] * _NUM_PORTS
        self._dragging = False
        self._has_can = False
    
    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not self._has_can:
                cr = self._can_rect()
                if cr and cr.collidepoint(event.pos):
                    self._has_can = True
            else:
                self._dragging = True
                self._try_lube(event.pos)
            
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._dragging = False
            
        if event.type == pygame.MOUSEMOTION and self._dragging and self._has_can:
            self._try_lube(event.pos)
    
    def update(self, dt: float) -> None:
        if all(self._lubed):
            self.complete()
    
    def draw(self, screen: pygame.Surface, content_rect: pygame.Rect) -> None:
        self._content_rect = content_rect
        font = view.font(10, "assets/fonts/IMFellEnglish-Regular.ttf")
        
        # draw engine body background
        body = pygame.Rect(
            content_rect.centerx - view.scale(120),
            content_rect.centery - view.scale(50),
            view.scale(240),
            view.scale(100),
        )
        pygame.draw.rect(screen, (50, 48, 62), body, border_radius=view.scale(8))
        pygame.draw.rect(screen, (80, 76, 100), body, width=max(1, view.scale(1)), border_radius=view.scale(8))
        
        # draw ports
        for i in range(_NUM_PORTS):
            r = self._port_rect(i)
            if r is None:
                continue
            lubed = self._lubed[i]
            col = (80, 160, 90) if lubed else (160, 140, 80)
            border = (120, 200, 130) if lubed else (100, 90, 60)
            pygame.draw.rect(screen, col, r, border_radius=view.scale(4))
            pygame.draw.rect(screen, border, r, width=max(1, view.scale(1)), border_radius=view.scale(4))
            
            lbl = font.render("✓" if lubed else f"P{i+1}", True, (240, 235, 210))
            screen.blit(lbl, (r.centerx - lbl.get_width() // 2, r.centery - lbl.get_height() // 2))
            
            # pipe stem below port
            stem_w = view.scale(6)
            stem_h = view.scale(14)
            stem = pygame.Rect(r.centerx - stem_w // 2, r.bottom, stem_w, stem_h)
            pygame.draw.rect(screen, (70, 68, 84), stem)
            
        # draw oil can or nozzle on cursor
        if not self._has_can:
            cr = self._can_rect()
            if cr:
                pygame.draw.rect(screen, (180, 150, 60), cr, border_radius=view.scale(4))
                pygame.draw.rect(screen, (210, 180, 80), cr, width=max(1, view.scale(1)), border_radius=view.scale(4))
                can_lbl = font.render("Oil Can", True, (240, 235, 210))
                screen.blit(can_lbl, (cr.centerx - can_lbl.get_width() // 2,
                                      cr.top - can_lbl.get_height() - view.scale(4)))
        else:
            mx, my = pygame.mouse.get_pos()
            nr = view.scale(_NOZZLE_RADIUS)
            nozzle = pygame.Surface((nr * 2, nr * 2), pygame.SRCALPHA)
            pygame.draw.circle(nozzle, (180, 150, 60, 220), (nr, nr), nr)
            pygame.draw.circle(nozzle, (210, 180, 80, 255), (nr, nr), nr, max(1, view.scale(1)))
            screen.blit(nozzle, (mx - nr, my - nr))
            
        # hint
        if not self._has_can:
            hint_text, hint_col = "Pick up the oil can.", (150, 146, 164)
        elif all(self._lubed):
            hint_text, hint_col = "Engine lubricated.", (172, 200, 150)
        else:
            remaining = _NUM_PORTS - sum(self._lubed)
            hint_text = f"Drag the nozzle over each port. {remaining} left."
            hint_col = (150, 146, 164)
        self.draw_hint(screen, content_rect, hint_text, hint_col)
        
    def _port_rect(self, idx: int) -> pygame.Rect | None:
        cr = self._content_rect
        if cr is None:
            return None
        pw, ph = view.scale(34), view.scale(28)
        total = _NUM_PORTS * pw + (_NUM_PORTS - 1) * view.scale(18)
        start_x = cr.centerx - total // 2
        x = start_x + idx * (pw + view.scale(18))
        y = cr.centery - ph // 2 - view.scale(6)
        return pygame.Rect(x, y, pw, ph)
        
    def _can_rect(self) -> pygame.Rect | None:
        cr = self._content_rect
        if cr is None:
            return None
        w, h = view.scale(40), view.scale(26)
        return pygame.Rect(cr.right - w - view.scale(20), cr.centery - h // 2, w, h)
    
    def _try_lube(self, pos) -> None:
        nr = view.scale(_NOZZLE_RADIUS)
        for i in range(_NUM_PORTS):
            if self._lubed[i]:
                continue
            r = self._port_rect(i)
            if r is None:
                continue
            expanded = r.inflate(nr * 2, nr * 2)
            if expanded.collidepoint(pos):
                self._lubed[i] = True


instance = LubricateEngine()