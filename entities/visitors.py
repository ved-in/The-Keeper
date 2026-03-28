import pygame
import core.view as view
import ui.dialogue as dialogue
from entities.interactables import Interactable
import entities.animations as animations
import entities.player as player

INTERACT_RANGE = 120  # max world-x distance to trigger dialogue

class Visitor(Interactable):
    def __init__(self, name, world_x, y, y_offset, lines_by_day, anim_folder=None, anim_scale=1.0, anim_key=None):
        super().__init__(name, world_x, y, 24, 40, lines_by_day, color=(180, 160, 140))
        self.talked_today = False
        
        # if anim_key is provided directly, use that instead of auto-registering
        if anim_key:
            self.anim_key = anim_key
        elif anim_folder:
            # legacy support for folder-based registration
            self.anim_key = f"visitor_{name.lower().replace(' ', '_')}"
            animations.register(self.anim_key, "idle", anim_folder, scale=anim_scale)
        else:
            self.anim_key = None
        
        self.y_offset = y_offset
        
    def reset_daily(self):
        self.talked_today = False
    
    def handle_click(self, pos, world_offset, day):
        if not self.is_on_screen(world_offset):
            return False
        if self.screen_rect(world_offset).collidepoint(pos):
            p = player._player
            if p is not None:
                player_world_x = p["x"] - player._world_offset
                if abs(player_world_x - self.world_x) > INTERACT_RANGE:
                    return False
            lines = self.lines_by_day.get(day, self.lines_by_day.get("default", ["..."]))
            dialogue.show(lines, style="thought", reveal_speed=40, npc_rect=self.screen_rect(world_offset))
            self.talked_today = True
            return True
        return False
    
    def draw(self, screen, world_offset, font=None, anim_state="idle", flip=False, highlight=False, highlight_color=(172, 152, 108)):
        rect = self.screen_rect(world_offset)
        if highlight and self.is_on_screen(world_offset):
            from entities.interactables import _draw_marker
            _draw_marker(screen, rect, highlight_color)
        
        if self.anim_key:
            frame = animations.get_frame(self.anim_key, anim_state, flip=flip)
            if frame:
                # align sprite bottom to the rect bottom (standing on ground)
                y_offset = int(round(self.y_offset * (view.current_scale() / view.reference_scale())))
                screen.blit(frame, (rect.centerx - frame.get_width() // 2, rect.bottom - frame.get_height() + y_offset))
        else:
            color = (120, 110, 100) if self.talked_today else self.color
            pygame.draw.rect(screen, color, rect, border_radius=3)
        if font:
            label = font.render(self.name, True, (240, 235, 210))
            outline = font.render(self.name, True, (0, 0, 0))
            lx = rect.centerx - label.get_width() // 2
            ly = rect.top - label.get_height()
            for ox, oy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
                screen.blit(outline, (lx + ox, ly + oy))
            screen.blit(label, (lx, ly))
