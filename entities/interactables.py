import math
import pygame
import core.view as view
import ui.dialogue as dialogue
import entities.animations as animations

import core.sound as sound

from typing import Optional, Callable


def _draw_bounce_arrow(screen, rect):
    t = pygame.time.get_ticks() / 1000.0
    bob = int(math.sin(t * 4.0) * view.scale(4))
    cx = rect.centerx
    tip_y = rect.top - view.scale(26) + bob
    half_w = view.scale(6)
    arrow_h = view.scale(7)
    col = (255, 230, 80)
    outline_col = (0, 0, 0)
    pts = [
        (cx,            tip_y + arrow_h),
        (cx - half_w,  tip_y),
        (cx + half_w,  tip_y),
    ]
    o = view.scale(2)
    outline_pts = [
        (cx,               tip_y + arrow_h + o),
        (cx - half_w - o, tip_y - o),
        (cx + half_w + o, tip_y - o),
    ]
    pygame.draw.polygon(screen, outline_col, outline_pts)
    pygame.draw.polygon(screen, col, pts)
    # stem outline
    # stem outline: draw as a polygon, not a filled rect
    stem_outline_pts = [
        (cx - view.scale(2) - o, tip_y - 4 - o),
        (cx + view.scale(2) + o, tip_y - 4 - o),
        (cx + view.scale(2) + o, tip_y),
        (cx - view.scale(2) - o, tip_y),
    ]
    pygame.draw.polygon(screen, outline_col, stem_outline_pts)
    pygame.draw.rect(screen, col,
                    pygame.Rect(cx - view.scale(2), tip_y - 4,
                                view.scale(4), view.scale(5)))


class Interactable:    
    def __init__(self, name, world_x, y, w, h, lines_by_day, color=(140, 130, 120), anim_path=None, anim_scale=1.0, anim_key=None):
        self.name = name
        self.world_x = world_x
        self.y = y
        self.w = w
        self.h = h
        self.lines_by_day = lines_by_day  # { day: ["line1", ...] }
        self.color = color
        self.used_today = False
        self.hovered = False
        self.pending = False   # True when this object has an active task/dialogue today
        self.on_use: Optional[Callable[[], None]] = None # F__K PYLANCEEE
        
        # if anim_key is provided directly, use that instead of auto-registering
        if anim_key:
            self.anim_key = anim_key
        elif anim_path:
            self.anim_key = f"interactable_{name.lower().replace(' ', '_')}"
            animations.register(self.anim_key, "idle", anim_path, scale=anim_scale)
        else:
            self.anim_key = None
    
    def reset_daily(self):
        self.used_today = False
        
    def screen_rect(self, world_offset):
        cx = self.world_x + world_offset
        return view.rect(cx - self.w / 2, self.y - self.h / 2, self.w, self.h)
    
    def is_on_screen(self, world_offset):
        rect = self.screen_rect(world_offset)
        screen_rect = view.content_rect()
        return rect.colliderect(screen_rect)
    
    def handle_click(self, pos, world_offset, day):
        if not self.is_on_screen(world_offset):
            return False
        if self.screen_rect(world_offset).collidepoint(pos):
            sound.play_button()
            if hasattr(self, "on_use") and self.on_use:
                self.on_use()
                return True
            lines = self.lines_by_day.get(day, self.lines_by_day.get("default", ["..."]))
            dialogue.show(lines, style="thought", reveal_speed=40, default_speaker="player")
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
                # center the sprite on the rect center
                screen.blit(frame, (rect.centerx - frame.get_width() // 2, rect.centery - frame.get_height() // 2))
        else:
            # Only draw grey box for Light Motor, skip for Lens and Lighthouse Door
            if self.name not in ("Lens", "Lighthouse Door"):
                color = tuple(max(0, c - 40) for c in self.color) if self.used_today else self.color
                pygame.draw.rect(screen, color, rect, border_radius=3)
        if self.hovered and font:
            label = font.render(self.name, True, (240, 235, 210))
            outline = font.render(self.name, True, (0, 0, 0))
            lx = rect.centerx - label.get_width() // 2
            ly = rect.top - label.get_height() - 6
            for ox, oy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
                screen.blit(outline, (lx + ox, ly + oy))
            screen.blit(label, (lx, ly))
        # bouncing arrow when there's something to do and it hasn't been done yet
        if self.pending and not self.used_today:
            _draw_bounce_arrow(screen, rect)
