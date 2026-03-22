import pygame
import constants
import core.view as view

ELEMENTS_OFFSET = 0

def make_player():
    return {"x": 480.0, "y": 360.0, "w": 24, "h": 40}


def update(p, dt):
    global ELEMENTS_OFFSET
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]  or keys[pygame.K_a]:
        ELEMENTS_OFFSET += constants.SPEED * dt
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        ELEMENTS_OFFSET -= constants.SPEED * dt
        
    # Clamping player's x coords to the valid screen area
    p["x"] = max(0, min(p["x"], view.BASE_W - p["w"]))
    

def draw(screen, p):
    rect = view.rect(p["x"], p["y"], p["w"], p["h"])
    pygame.draw.rect(screen, (220, 200, 170), rect)
    return rect
