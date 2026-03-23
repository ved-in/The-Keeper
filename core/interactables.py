import pygame
import core.view as view
import ui.dialogue as dialogue
import core.animations as animations


class Interactable:    
    def __init__(self, name, world_x, y, w, h, lines_by_day, color=(140, 130, 120), anim_path=None, anim_scale=1.0):
        self.name = name
        self.world_x = world_x
        self.y = y
        self.w = w
        self.h = h
        self.lines_by_day = lines_by_day  # { day: ["line1", ...] }
        self.color = color
        self.used_today = False
        self.hovered = False
        
        self.anim_key = None
        if anim_path:
            self.anim_key = f"interactable_{name.lower().replace(' ', '_')}"
            animations.register(self.anim_key, "idle", anim_path, scale=anim_scale)
    
    def reset_daily(self):
        self.used_today = False
        
    def screen_rect(self, world_offset):
        return view.rect(self.world_x + world_offset, self.y, self.w, self.h)
    
    def handle_click(self, pos, world_offset, day):
        if self.screen_rect(world_offset).collidepoint(pos):
            lines = self.lines_by_day.get(day, self.lines_by_day.get("default", ["..."]))
            dialogue.show(lines, style="thought", reveal_speed=40)
            self.used_today = True
            return True
        return False
    
    def update(self, mouse_pos, world_offset):
        self.hovered = self.screen_rect(world_offset).collidepoint(mouse_pos)
        
    def draw(self, screen, world_offset, font=None):
        rect = self.screen_rect(world_offset)
        if self.anim_key:
            frame = animations.get_frame(self.anim_key, "idle")
            if frame:
                frame = pygame.transform.scale(frame, (rect.width, rect.height))
                screen.blit(frame, rect)
        else:
            color = tuple(max(0, c - 40) for c in self.color) if self.used_today else self.color
            pygame.draw.rect(screen, color, rect, border_radius=3)
        if self.hovered and font:
            label = font.render(self.name, True, (240, 235, 210))
            screen.blit(label, (rect.centerx - label.get_width() // 2, rect.top - label.get_height() - 4))
            