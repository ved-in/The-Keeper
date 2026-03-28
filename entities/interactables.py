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
        self.pending = False
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
        
    def draw(self, screen, world_offset, font=None, highlight=False, highlight_color=(172, 152, 108)):
        rect = self.screen_rect(world_offset)
        if highlight and self.is_on_screen(world_offset):
            _draw_marker(screen, rect, highlight_color)
        if self.anim_key:
            frame = animations.get_frame(self.anim_key, "idle")
            if frame:
                # center the sprite on the rect center
                screen.blit(frame, (rect.centerx - frame.get_width() // 2, rect.centery - frame.get_height() // 2))
        else:
            # Only draw grey box for Light Motor, skip for Lens, Lighthouse Door, and Engine
            if self.name not in ("Lens", "Lighthouse Door", "Engine"):
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
        if self.pending and not highlight and not self.used_today and self.is_on_screen(world_offset):
            _draw_bounce_arrow(screen, rect)


def _draw_marker(screen, rect, color):
    pulse = 0.5 + (math.sin(pygame.time.get_ticks() * 0.006) * 0.5)

    halo_w = rect.width + view.scale(16)
    halo_h = rect.height + view.scale(12)
    halo = pygame.Surface((halo_w, halo_h), pygame.SRCALPHA)
    pygame.draw.ellipse(
        halo,
        (*color, int(28 + 24 * pulse)),
        halo.get_rect(),
        width=max(1, view.scale(2)),
    )
    screen.blit(halo, (rect.centerx - halo_w // 2, rect.centery - halo_h // 2))

    size = view.scale(6)
    center_x = rect.centerx
    center_y = rect.top - view.scale(10) - int(pulse * view.scale(4))
    shadow_points = [
        (center_x, center_y - size + view.scale(2)),
        (center_x + size, center_y + view.scale(2)),
        (center_x, center_y + size + view.scale(2)),
        (center_x - size, center_y + view.scale(2)),
    ]
    points = [
        (center_x, center_y - size),
        (center_x + size, center_y),
        (center_x, center_y + size),
        (center_x - size, center_y),
    ]

    pygame.draw.polygon(screen, (20, 16, 16), shadow_points)
    pygame.draw.polygon(screen, color, points)
    pygame.draw.polygon(screen, (245, 236, 214), points, width=max(1, view.scale(1)))


def _draw_bounce_arrow(screen, rect):
    pulse = 0.5 + (math.sin(pygame.time.get_ticks() * 0.006) * 0.5)
    size = view.scale(6)
    center_x = rect.centerx
    center_y = rect.top - view.scale(18) - int(pulse * view.scale(5))

    shadow_points = [
        (center_x, center_y + size + view.scale(2)),
        (center_x + size, center_y - size + view.scale(2)),
        (center_x - size, center_y - size + view.scale(2)),
    ]
    points = [
        (center_x, center_y + size),
        (center_x + size, center_y - size),
        (center_x - size, center_y - size),
    ]

    pygame.draw.polygon(screen, (20, 16, 16), shadow_points)
    pygame.draw.polygon(screen, (214, 194, 122), points)
    pygame.draw.polygon(screen, (245, 236, 214), points, width=max(1, view.scale(1)))
