"""
Log Barometric Pressure minigame.

A barometer dial shows a pressure reading. Type the matching number into
the logbook field and press ENTER to confirm.
"""

import math
import random
import pygame
import core.view as view
from systems.minigame import Minigame


class LogPressure(Minigame):
    TITLE = "Log Barometric Pressure"
    def __init__(self) -> None:
        super().__init__()
        self._target: int = 0
        self._input_text: str = ""
        self._confirmed: bool = False
        self._wrong_flash: float = 0.0
        self._content_rect: pygame.Rect | None = None
    
    def reset(self) -> None:
        super().reset()
        self._target      = random.randint(960, 1040)
        self._input_text  = ""
        self._confirmed   = False
        self._wrong_flash = 0.0
    
    def handle_event(self, event: pygame.event.Event) -> None:
        if self._confirmed:
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self._input_text = self._input_text[:-1]
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                try:
                    val = int(self._input_text)
                except ValueError:
                    val = -1
                if val == self._target:
                    self._confirmed = True
                else:
                    self._input_text  = ""
                    self._wrong_flash = 1.0
            elif event.unicode.isdigit() and len(self._input_text) < 5:
                self._input_text += event.unicode
    
    def update(self, dt: float) -> None:
        if self._wrong_flash > 0:
            self._wrong_flash = max(0.0, self._wrong_flash - dt * 3)
        if self._confirmed:
            self.complete()
    
    def draw(self, screen: pygame.Surface, content_rect: pygame.Rect) -> None:
        self._content_rect = content_rect
        font     = view.font(10, "assets/fonts/IMFellEnglish-Regular.ttf")
        font_big = view.font(14, "assets/fonts/IMFellEnglish-Regular.ttf")
        
        # barometer dial
        dial_cx = content_rect.left + int(content_rect.width * 0.30)
        dial_cy = content_rect.centery - view.scale(4)
        dial_r  = view.scale(44)
        
        pygame.draw.circle(screen, (38, 34, 50), (dial_cx, dial_cy), dial_r)
        pygame.draw.circle(screen, (100, 96, 116), (dial_cx, dial_cy), dial_r, max(1, view.scale(1)))

        for i in range(9):
            t     = i / 8
            angle = math.pi * (0.75 + t * 1.5)
            ix = dial_cx + int(math.cos(angle) * (dial_r - view.scale(8)))
            iy = dial_cy + int(math.sin(angle) * (dial_r - view.scale(8)))
            ox = dial_cx + int(math.cos(angle) * (dial_r - view.scale(2)))
            oy = dial_cy + int(math.sin(angle) * (dial_r - view.scale(2)))
            pygame.draw.line(screen, (160, 156, 176), (ix, iy), (ox, oy), max(1, view.scale(1)))

        t_norm  = (self._target - 960) / 80
        n_angle = math.pi * (0.75 + t_norm * 1.5)
        nx = dial_cx + int(math.cos(n_angle) * (dial_r - view.scale(10)))
        ny = dial_cy + int(math.sin(n_angle) * (dial_r - view.scale(10)))
        pygame.draw.line(screen, (210, 80, 80), (dial_cx, dial_cy), (nx, ny), max(2, view.scale(2)))
        pygame.draw.circle(screen, (180, 60, 60), (dial_cx, dial_cy), view.scale(4))

        rdg = font.render(f"{self._target} hPa", True, (200, 196, 210))
        screen.blit(rdg, (dial_cx - rdg.get_width() // 2, dial_cy + dial_r + view.scale(4)))
        ttl = font.render("BAROMETER", True, (150, 146, 164))
        screen.blit(ttl, (dial_cx - ttl.get_width() // 2, dial_cy - dial_r - ttl.get_height() - view.scale(2)))

        # logbook
        book_x = content_rect.left + int(content_rect.width * 0.61)
        book_w = int(content_rect.width * 0.28)
        book_h = int(content_rect.height * 0.40)
        book   = pygame.Rect(book_x, content_rect.centery - book_h // 2, book_w, book_h)

        pygame.draw.rect(screen, (228, 220, 198), book, border_radius=view.scale(4))
        pygame.draw.rect(screen, (112, 96, 92), book, width=max(1, view.scale(1)), border_radius=view.scale(4))

        log_t = font.render("KEEPER'S LOG", True, (112, 96, 92))
        screen.blit(log_t, (book.centerx - log_t.get_width() // 2, book.top + view.scale(8)))

        line_y = book.top + view.scale(26)
        while line_y < book.bottom - view.scale(10):
            pygame.draw.line(screen, (180, 168, 148), (book.left + view.scale(8), line_y), (book.right - view.scale(8), line_y), 1)
            line_y += view.scale(14)

        field = pygame.Rect(book.left + view.scale(8), book.centery - view.scale(14), book.width - view.scale(16), view.scale(28))
        field_col = (255, 100, 80) if self._wrong_flash > 0.3 else (210, 200, 178)
        pygame.draw.rect(screen, field_col, field, border_radius=view.scale(3))
        pygame.draw.rect(screen, (112, 96, 92), field, width=max(1, view.scale(1)), border_radius=view.scale(3))

        entry_text = f"{self._target} hPa" if self._confirmed else (self._input_text + "|")
        entry_col  = (40, 120, 60) if self._confirmed else (34, 30, 36)
        entry_surf = font_big.render(entry_text, True, entry_col)
        screen.blit(entry_surf, (field.left + view.scale(6), field.centery - entry_surf.get_height() // 2))
        
        eh = font.render("ENTER to confirm", True, (130, 120, 108))
        screen.blit(eh, (book.centerx - eh.get_width() // 2, field.bottom + view.scale(6)))
        
        if self._confirmed:
            hint_text, hint_col = "Reading logged.", (172, 200, 150)
        elif self._wrong_flash > 0:
            hint_text, hint_col = "Incorrect. Read the dial carefully.", (210, 100, 100)
        else:
            hint_text, hint_col = "Type the pressure shown on the barometer.", (150, 146, 164)
        self.draw_hint(screen, content_rect, hint_text, hint_col)


instance = LogPressure()
