import pygame
import core.view as view
import ui.dialogue as dialogue


class Interactable:    
    def __init__(self, name, world_x, y, w, h, lines_by_day, color=(140, 130, 120)):
        self.name = name
        self.world_x = world_x
        self.y = y
        self.w = w
        self.h = h
        self.lines_by_day = lines_by_day  # { day: ["line1", ...] }
        self.color = color
        self.used_today = False
        self.hovered = False
    
    def reset_daily(self):
        self.used_today = False
        
    def screen_rect(self, world_offset):
        return view.rect(self.world_x + world_offset, self.y, self.w, self.h)
    
    def handle_click(self, pos, world_offset, day):
        if self.screen_rect(world_offset).collidepoint(pos):
            lines = self.lines_by_day.get(day, self.lines_by_day.get("default", ["..."]))
            dialogue.show(lines, style="thought")
            self.used_today = True
            return True
        return False
    
    def update(self, mouse_pos, world_offset):
        self.hovered = self.screen_rect(world_offset).collidepoint(mouse_pos)
        
    def draw(self, screen, world_offset, font=None):
        rect = self.screen_rect(world_offset)
        color = tuple(max(0, c - 40) for c in self.color) if self.used_today else self.color
        pygame.draw.rect(screen, color, rect, border_radius=3)
        
        if self.hovered and font:
            label = font.render(self.name, True, (240, 235, 210))
            screen.blit(label, (rect.centerx - label.get_width() // 2, rect.top - label.get_height() - 4))
            