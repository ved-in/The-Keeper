import pygame

SPEED = 200

def make_player():
    return {"x": 480.0, "y": 360.0, "w": 24, "h": 40}


def update(p, dt):
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]  or keys[pygame.K_a]:
        p["x"] -= SPEED * dt
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        p["x"] += SPEED * dt
        
    # Clamping player's x coords to the valid screen area
    p["x"] = max(0, min(p["x"], 960 - p["w"]))
    

def draw(screen, p):
    rect = pygame.Rect(int(p["x"]), int(p["y"]), p["w"], p["h"])
    pygame.draw.rect(screen, (220, 200, 170), rect)
    