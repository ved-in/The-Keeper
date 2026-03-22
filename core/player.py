import pygame
import os
import math
import constants
import core.view as view
import core.animations as animations

_world_offset = 0.0
_pointer_img = None

def make_player():
    return {"x": 480.0, "y": 360.0, "w": 24, "h": 40, "target_world_x": None}

def reset_world():
    global _world_offset
    _world_offset = 0.0

def world_x(x_pos):
    return x_pos + _world_offset

def update(p, dt):
    global _world_offset
    
    # keys = pygame.key.get_pressed()
    # direction = int(keys[pygame.K_LEFT] or keys[pygame.K_a]) - int(keys[pygame.K_RIGHT] or keys[pygame.K_d])
    
    ground_start = -250
    ground_end = ground_start + view.BASE_W
    
    mouse_pressed = pygame.mouse.get_pressed()
    if mouse_pressed[0]:
        #get_pos()[0] to grab only x coordinate of click
        raw_mouse_x = pygame.mouse.get_pos()[0] 
        
        #translate the x coordinate back to base resolution
        base_mouse_x = view.un_x(raw_mouse_x) 
        
        #calculate raw click in the world
        clicked_world_x = base_mouse_x - _world_offset
        
        #clamp the target so the pointer doesnt spawn outside walkable area
        max_walkable_x = ground_end - p["w"]
        p["target_world_x"] = max(ground_start, min(clicked_world_x, max_walkable_x))

    direction = 0
    if p.get("target_world_x") is not None:
        player_world_x = p["x"] - _world_offset
        distance = p["target_world_x"] - player_world_x

        move_step = constants.SPEED * dt
        if abs(distance) <= move_step:
            p["target_world_x"] = None
            direction = 0
        else:
            direction = -1 if distance > 0 else 1

    new_state = "walk" if direction else "idle"
    if p.get("anim_state") != new_state:
        p["anim_state"] = new_state
        animations.reset("mc")
    
    p["moving"] = bool(direction)
    p["facing_left"] = direction > 0 if direction else p.get("facing_left", False)
    
    if not direction:
        return

    min_offset = -(ground_end - p["w"] - p["x"])
    max_offset = p["x"] - ground_start
    
    old_offset = _world_offset
    _world_offset = max(min_offset, min(_world_offset + (direction * constants.SPEED * dt), max_offset))

    if old_offset == _world_offset and direction != 0:
        p["target_world_x"] = None


def draw(screen, p):
    global _pointer_img

    if p.get("target_world_x") is not None:
        if _pointer_img is None:
            path = os.path.join("assets", "sprites", "pointer.png")
            try:
                _pointer_img = pygame.image.load(path).convert_alpha()
            except FileNotFoundError:
                _pointer_img = pygame.Surface((10, 10))
                _pointer_img.fill((255, 0, 0))

        pointer_screen_x = p["target_world_x"] + _world_offset
        
        p_speed = 0.005 #pointer hover speed
        p_height = 4 #pointer hover height
        hover_offset = math.sin(pygame.time.get_ticks() * p_speed) * p_height
        
        pointer_screen_y = (p["y"] + p["h"]) - hover_offset 

        pointer_pos = view.point(pointer_screen_x, pointer_screen_y)
        
        rect = _pointer_img.get_rect(midbottom=pointer_pos) 
        screen.blit(_pointer_img, rect)

    frame = animations.get_frame("mc", "walk" if p.get("moving") else "idle", flip=p.get("facing_left", False))
    pos = view.point(p["x"], p["y"])
    if frame:
        screen.blit(frame, pos)
    else:
        pygame.draw.rect(screen, (220, 200, 170), view.rect(p["x"], p["y"], p["w"], p["h"]))
