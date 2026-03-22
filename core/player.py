import pygame
import constants
import core.view as view

_world_offset = 0.0


def make_player():
    return {"x": 480.0, "y": 360.0, "w": 24, "h": 40}


def reset_world():
    global _world_offset
    _world_offset = 0.0


def world_x(x_pos):
    return x_pos + _world_offset


def update(p, dt):
    global _world_offset
    keys = pygame.key.get_pressed()
    direction = int(keys[pygame.K_LEFT] or keys[pygame.K_a]) - int(keys[pygame.K_RIGHT] or keys[pygame.K_d])
    if not direction:
        return

    min_offset = -(view.BASE_W - p["w"] - p["x"])
    max_offset = p["x"]
    _world_offset = max(min_offset, min(_world_offset + (direction * constants.SPEED * dt), max_offset))


def draw(screen, p):
    rect = view.rect(p["x"], p["y"], p["w"], p["h"])
    pygame.draw.rect(screen, (220, 200, 170), rect)
    return rect
