"""
Clean the Lens minigame.

Pick up the rag, then drag it across the lens to wipe away all the dust.
"""

import pygame
import core.view as view
from systems.minigame import Minigame

DUST_COLS = 21
DUST_ROWS = 12


class CleanLens(Minigame):
    TITLE = "Clean the Lens"
    def __init__(self) -> None:
        super().__init__()
        self._has_rag: bool = False
        self._dragging: bool = False
        self._dust: list[list[bool]] = []
        self._content_rect: pygame.Rect | None = None
    
    def reset(self) -> None:
        super().reset()
        self._has_rag = False
        self._dragging = False
        self._dust = [[True] * DUST_COLS for _ in range(DUST_ROWS)]
    
    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            if not self._has_rag:
                rr = self._rag_rect()
                if rr and rr.collidepoint(pos):
                    self._has_rag = True
            else:
                lr = self._lens_rect()
                if lr and lr.collidepoint(pos):
                    self._dragging = True
                    self._wipe_at(pos)
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._dragging = False
        if event.type == pygame.MOUSEMOTION and self._dragging and self._has_rag:
            self._wipe_at(event.pos)
    
    def update(self, dt: float) -> None:
        if self._all_clean():
            self.complete()
    
    def draw(self, screen: pygame.Surface, content_rect: pygame.Rect) -> None:
        self._content_rect = content_rect
        font = view.font(10, "assets/fonts/IMFellEnglish-Regular.ttf")

        lr = self._lens_rect()
        pygame.draw.rect(screen, (190, 215, 235), lr, border_radius=view.scale(6))

        for row in range(DUST_ROWS):
            for col in range(DUST_COLS):
                if self._dust[row][col]:
                    cell = self._dust_cell_rect(col, row)
                    if cell is None:
                        continue
                    dust_surf = pygame.Surface((cell.width, cell.height), pygame.SRCALPHA)
                    dust_surf.fill((180, 155, 90, 170))
                    screen.blit(dust_surf, cell)

        pygame.draw.rect(screen, (120, 140, 160), lr, width=max(1, view.scale(1)), border_radius=view.scale(6))
        lbl = font.render("Lens", True, (50, 50, 70))
        screen.blit(lbl, (lr.centerx - lbl.get_width() // 2, lr.top - lbl.get_height() - view.scale(4)))

        if not self._has_rag:
            hint_text, hint_col = "Pick up the rag first.", (150, 146, 164)
        elif not self._all_clean():
            hint_text, hint_col = "Drag the rag across the lens to clean it.", (150, 146, 164)
        else:
            hint_text, hint_col = "Lens is clean!", (172, 200, 150)
        self.draw_hint(screen, content_rect, hint_text, hint_col)

        if not self._has_rag:
            rr = self._rag_rect()
            pygame.draw.rect(screen, (180, 160, 130), rr, border_radius=view.scale(3))
            lbl = font.render("Rag", True, (240, 235, 210))
            screen.blit(lbl, (rr.centerx - lbl.get_width() // 2, rr.top - lbl.get_height() - view.scale(4)))
        else:
            mx, my = pygame.mouse.get_pos()
            rw, rh = view.scale(28), view.scale(18)
            rag_surf = pygame.Surface((rw, rh), pygame.SRCALPHA)
            rag_surf.fill((180, 160, 130, 200))
            screen.blit(rag_surf, (mx - rw // 2, my - rh // 2))
    

    def _rag_rect(self) -> pygame.Rect | None:
        cr = self._content_rect
        if cr is None:
            return None
        rw, rh = view.scale(36), view.scale(22)
        return pygame.Rect(cr.x + view.scale(24), cr.centery - rh // 2, rw, rh)
    
    def _lens_rect(self) -> pygame.Rect | None:
        cr = self._content_rect
        if cr is None:
            return None
        lw = int(cr.width * 0.55)
        lh = int(cr.height * 0.72)
        return pygame.Rect(cr.centerx - lw // 2 + view.scale(20), cr.centery - lh // 2, lw, lh)
    
    def _dust_cell_rect(self, col: int, row: int) -> pygame.Rect | None:
        lr = self._lens_rect()
        if lr is None:
            return None
        cw = lr.width  // DUST_COLS
        ch = lr.height // DUST_ROWS
        return pygame.Rect(lr.x + col * cw, lr.y + row * ch, cw, ch)
    
    def _all_clean(self) -> bool:
        return not any(cell for row in self._dust for cell in row)
    
    def _wipe_at(self, pos) -> None:
        for row in range(DUST_ROWS):
            for col in range(DUST_COLS):
                if self._dust[row][col]:
                    cell = self._dust_cell_rect(col, row)
                    if cell and cell.collidepoint(pos):
                        self._dust[row][col] = False


instance = CleanLens()