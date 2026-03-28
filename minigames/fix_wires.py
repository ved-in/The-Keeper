"""
Fix Generator Wires minigame.

Three frayed wires hang on the left. Drag each wire end to its matching
coloured slot on the right to complete the circuit.
"""

import pygame
import core.view as view
from systems.minigame import Minigame

import core.sound as sound

_WIRE_DEFS = [
    {"color": (210, 80,  80),  "label": "R"},
    {"color": (80,  180, 100), "label": "G"},
    {"color": (80,  130, 210), "label": "B"},
]


class FixWires(Minigame):
    TITLE = "Reconnect the Wires"
    def __init__(self) -> None:
        super().__init__()
        self._connected: list[bool] = [False, False, False]
        self._dragging_idx: int | None = None
        self._drag_pos: tuple[int, int] = (0, 0)
        self._content_rect: pygame.Rect | None = None
    
    def reset(self) -> None:
        super().reset()
        self._connected = [False, False, False]
        self._dragging_idx = None
        

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            for i in range(3):
                if not self._connected[i]:
                    tip = self._wire_tip(i)
                    if tip and self._circle_hit(pos, tip, view.scale(10)):
                        self._dragging_idx = i
                        self._drag_pos = pos
                        return
        
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self._dragging_idx is not None:
                slot = self._slot_rect(self._dragging_idx)
                if slot and slot.collidepoint(event.pos):
                    self._connected[self._dragging_idx] = True
                    sound.play_wire_connect()
                self._dragging_idx = None
        
        if event.type == pygame.MOUSEMOTION and self._dragging_idx is not None:
            self._drag_pos = event.pos
    
    def update(self, dt: float) -> None:
        if all(self._connected):
            self.complete()
    
    def draw(self, screen: pygame.Surface, content_rect: pygame.Rect) -> None:
        self._content_rect = content_rect
        font = view.font(10, "assets/fonts/IMFellEnglish-Regular.ttf")

        for i in range(3):
            color = _WIRE_DEFS[i]["color"]
            dim   = tuple(max(0, c - 60) for c in color)

            slot = self._slot_rect(i)
            if slot:
                slot_color = color if self._connected[i] else (50, 48, 58)
                pygame.draw.rect(screen, slot_color, slot, border_radius=view.scale(4))
                pygame.draw.rect(screen, (100, 96, 116), slot, width=max(1, view.scale(1)), border_radius=view.scale(4))
                lbl = font.render(_WIRE_DEFS[i]["label"], True, (240, 235, 210))
                screen.blit(lbl, (slot.centerx - lbl.get_width() // 2, slot.centery - lbl.get_height() // 2))
            
            anchor = self._wire_anchor(i)
            tip    = self._wire_tip(i)
            if anchor and tip:
                if self._connected[i]:
                    end = self._slot_rect(i).center
                    pygame.draw.line(screen, dim, anchor, end, max(2, view.scale(2)))
                elif self._dragging_idx == i:
                    pygame.draw.line(screen, color, anchor, self._drag_pos, max(2, view.scale(2)))
                    pygame.draw.circle(screen, color, self._drag_pos, view.scale(8))
                    pygame.draw.circle(screen, (240, 235, 210), self._drag_pos, view.scale(8), max(1, view.scale(1)))
                else:
                    pygame.draw.line(screen, color, anchor, tip, max(2, view.scale(2)))
                    pygame.draw.circle(screen, color, tip, view.scale(8))
                    pygame.draw.circle(screen, (240, 235, 210), tip, view.scale(8), max(1, view.scale(1)))
        
        if all(self._connected):
            hint_text, hint_col = "All wires connected!", (172, 200, 150)
        elif self._dragging_idx is not None:
            hint_text, hint_col = "Drop onto the matching slot.", (150, 146, 164)
        else:
            hint_text, hint_col = "Drag each wire to its matching slot.", (150, 146, 164)
        self.draw_hint(screen, content_rect, hint_text, hint_col)
    
    def _wire_anchor(self, idx: int) -> tuple[int, int] | None:
        cr = self._content_rect
        if cr is None:
            return None
        spacing = cr.height // 4
        return (cr.left + view.scale(20), cr.top + spacing * (idx + 1))

    def _wire_tip(self, idx: int) -> tuple[int, int] | None:
        anchor = self._wire_anchor(idx)
        if anchor is None:
            return None
        return (anchor[0] + view.scale(60), anchor[1] + view.scale(idx * 8 - 8))

    def _slot_rect(self, idx: int) -> pygame.Rect | None:
        cr = self._content_rect
        if cr is None:
            return None
        sw, sh = view.scale(32), view.scale(22)
        spacing = cr.height // 4
        y = cr.top + spacing * (idx + 1) - sh // 2
        x = cr.right - sw - view.scale(24)
        return pygame.Rect(x, y, sw, sh)
    
    @staticmethod
    def _circle_hit(pos, center, radius) -> bool:
        dx = pos[0] - center[0]
        dy = pos[1] - center[1]
        return dx * dx + dy * dy <= radius * radius


instance = FixWires()
