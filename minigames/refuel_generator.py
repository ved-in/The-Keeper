"""
Refuel Generator minigame.

Hold the pump button to fill the tank. Release and it stops.
Tank full = complete.
"""

import pygame
import core.view as view
from systems.minigame import Minigame

FILL_SPEED = 0.45  # fraction per second while held


class RefuelGenerator(Minigame):
    TITLE = "Refuel Generator"
    def __init__(self) -> None:
        super().__init__()
        self._level: float = 0.0
        self._holding: bool = False
        self._content_rect: pygame.Rect | None = None
    
    def reset(self) -> None:
        super().reset()
        self._level = 0.0
        self._holding = False
        
    def handle_event(self, event: pygame.event.Event) -> None:
        btn = self._button_rect()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if btn and btn.collidepoint(event.pos):
                self._holding = True
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._holding = False
        
    def update(self, dt: float) -> None:
        if self._holding and self._level < 1.0:
            self._level = min(1.0, self._level + FILL_SPEED * dt)
        if self._level >= 1.0:
            self.complete()
        
    def draw(self, screen: pygame.Surface, content_rect: pygame.Rect) -> None:
        self._content_rect = content_rect
        font = view.font(10, "assets/fonts/IMFellEnglish-Regular.ttf")
        
        tank = self._tank_rect()
        if tank is None:
            return
        
        # tank body
        pygame.draw.rect(screen, (30, 28, 40), tank, border_radius=view.scale(6))
        pygame.draw.rect(screen, (80, 76, 100), tank,
                         width=max(1, view.scale(1)), border_radius=view.scale(6))
        
        # fuel fill from bottom
        if self._level > 0:
            fill_h = int(tank.height * self._level)
            fill = pygame.Rect(tank.left + max(1, view.scale(1)),
                               tank.bottom - fill_h,
                               tank.width - max(2, view.scale(2)),
                               fill_h)
            t = self._level
            fill_col = (min(255, int(60 + 140 * t)), max(0, int(160 - 80 * t)), 60)
            br = view.scale(5)
            pygame.draw.rect(screen, fill_col, fill,
                             border_bottom_left_radius=br,
                             border_bottom_right_radius=br)
        
        # percentage
        pct = font.render(f"{int(self._level * 100)}%", True, (230, 225, 210))
        screen.blit(pct, (tank.centerx - pct.get_width() // 2,
                          tank.centery - pct.get_height() // 2))
        
        # label above tank
        lbl = font.render("FUEL TANK", True, (150, 146, 164))
        screen.blit(lbl, (tank.centerx - lbl.get_width() // 2,
                          tank.top - lbl.get_height() - view.scale(6)))
        
        # pump button
        btn = self._button_rect()
        if btn:
            btn_col    = (60, 110, 60) if self._holding else (40, 70, 40)
            btn_border = (100, 180, 100) if self._holding else (70, 110, 70)
            pygame.draw.rect(screen, btn_col, btn, border_radius=view.scale(5))
            pygame.draw.rect(screen, btn_border, btn,
                             width=max(1, view.scale(1)), border_radius=view.scale(5))
            label = "PUMPING..." if self._holding else "HOLD TO PUMP"
            if self._level >= 1.0:
                label = "FULL"
            btn_lbl = font.render(label, True, (200, 240, 200))
            screen.blit(btn_lbl, (btn.centerx - btn_lbl.get_width() // 2,
                                  btn.centery - btn_lbl.get_height() // 2))
        
        if self._level < 1.0:
            hint_text = "Hold the button to pump fuel into the generator."
            hint_col  = (150, 146, 164)
        else:
            hint_text = "Generator refuelled."
            hint_col  = (172, 200, 150)
        self.draw_hint(screen, content_rect, hint_text, hint_col)
    
    def _tank_rect(self) -> pygame.Rect | None:
        cr = self._content_rect
        if cr is None:
            return None
        w, h = view.scale(60), view.scale(130)
        return pygame.Rect(cr.centerx - w // 2, cr.centery - h // 2 - view.scale(16), w, h)
    
    def _button_rect(self) -> pygame.Rect | None:
        tank = self._tank_rect()
        cr   = self._content_rect
        if tank is None or cr is None:
            return None
        w, h = view.scale(130), view.scale(36)
        return pygame.Rect(cr.centerx - w // 2, tank.bottom + view.scale(14), w, h)


instance = RefuelGenerator()