import pygame
import ui.dialogue as dialogue
from core.interactables import Interactable

class Visitor(Interactable):
    def __init__(self, name, world_x, y, lines_by_day):
        super().__init__(name, world_x, y, 24, 40, lines_by_day, color=(180, 160, 140))
        self.talked_today = False
        
    def reset_daily(self):
        self.used_today = False
        self.talked_today = False
    
    def handle_click(self, pos, world_offset, day):
        if self.screen_rect(world_offset).collidepoint(pos):
            lines = self.lines_by_day.get(day, self.lines_by_day.get("default", ["..."]))
            dialogue.show(lines, style="thought")
            self.used_today = True
            self.talked_today = True
            return True
        return False
    
    def draw(self, screen, world_offset, font=None):
        rect = self.screen_rect(world_offset)
        color = (120, 110, 100) if self.talked_today else self.color
        pygame.draw.rect(screen, color, rect, border_radius=3)
        
        if font:
            label = font.render(self.name, True, (240, 235, 210))
            screen.blit(label, (rect.centerx - label.get_width() // 2, rect.top - label.get_height() - 4))
            