import pygame
import constants
import core.view as view
import core.animations as animations

# how far the world has scrolled horizontally
# negative means scrolled right, positive means scrolled left
_world_offset = 0.0


def make_player():
    # x and y are the fixed screen position of the player rectangle
    # the player never actually moves on screen, the world scrolls around them
    return {"x": 480.0, "y": 360.0, "w": 24, "h": 40}


def reset_world():
    # call this when switching scenes so the scroll position starts fresh
    global _world_offset
    _world_offset = 0.0


def world_x(x_pos):
    # converts a world position to a screen position by adding the scroll offset
    return x_pos + _world_offset


def update(p, dt):
    global _world_offset

    keys = pygame.key.get_pressed()
    # direction is 1 when moving left, -1 when moving right, 0 when still
    direction = int(keys[pygame.K_LEFT] or keys[pygame.K_a]) - int(keys[pygame.K_RIGHT] or keys[pygame.K_d])
    
    # switch animation state and reset the frame counter when the state changes
    new_state = "walk" if direction else "idle"
    if p.get("anim_state") != new_state:
        p["anim_state"] = new_state
        animations.reset("mc")  # reset frame to 0 on state change
    
    p["moving"] = bool(direction)
    # keep the last facing direction so the sprite does not flip back when idle
    p["facing_left"] = direction > 0 if direction else p.get("facing_left", False)
    
    if not direction:
        return

    # clamp the scroll so the player cannot walk past the edges of the ground rect
    ground_start = -250
    ground_end = ground_start + view.BASE_W
    
    min_offset = -(ground_end - p["w"] - p["x"])
    max_offset = p["x"] - ground_start
    _world_offset = max(min_offset, min(_world_offset + (direction * constants.SPEED * dt), max_offset))


def draw(screen, p):
    # use the walk frames when moving, idle frames when standing still
    frame = animations.get_frame("mc", "walk" if p.get("moving") else "idle", flip=p.get("facing_left", False))
    pos = view.point(p["x"], p["y"])
    if frame:
        screen.blit(frame, pos)
    else:
        # fallback coloured rectangle if the sprite sheets failed to load
        pygame.draw.rect(screen, (220, 200, 170), view.rect(p["x"], p["y"], p["w"], p["h"]))
