import pygame
import ui.dialogue as dialogue
from core.interactables import Interactable
import core.animations as animations

class Visitor(Interactable):
    def __init__(self, name, world_x, y, x_offset, y_offset, lines_by_day, anim_folder=None, anim_scale=1.0):
        super().__init__(name, world_x, y, 24, 40, lines_by_day, color=(180, 160, 140))
        self.talked_today = False
        
        self.anim_key = None
        if anim_folder:
            self.anim_key = f"visitor_{name.lower().replace(' ', '_')}"
            animations.register(self.anim_key, "idle", anim_folder, scale=anim_scale)
            
        self.x_offset = x_offset
        self.y_offset = y_offset
        
    def reset_daily(self):
        self.talked_today = False
    
    def handle_click(self, pos, world_offset, day):
        if self.screen_rect(world_offset).collidepoint(pos):
            lines = self.lines_by_day.get(day, self.lines_by_day.get("default", ["..."]))
            dialogue.show(lines, style="thought", reveal_speed=40)
            self.talked_today = True
            return True
        return False
    
    def draw(self, screen, world_offset, font=None):
        rect = self.screen_rect(world_offset)
        draw_rect = rect.move(0, self.y_offset)
        
        if self.anim_key:
            frame = animations.get_frame(self.anim_key, "idle")
            if frame:
                screen.blit(frame, (rect.x + self.x_offset, rect.y + self.y_offset))
        else:
            color = (120, 110, 100) if self.talked_today else self.color
            pygame.draw.rect(screen, color, rect, border_radius=3)
        if font:
            label = font.render(self.name, True, (240, 235, 210))
            screen.blit(label, (draw_rect.centerx - label.get_width() // 2, draw_rect.top - label.get_height() - 4))
            