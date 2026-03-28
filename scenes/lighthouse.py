import math
import random
import pygame
import entities.player as player
import constants
import core.view as view
import pytmx

GROUND = (-250, constants.GROUND_Y, view.BASE_W, 140)

# Lighthouse Sprite Properties
SPRITE_X = 400
SPRITE_Y = 100
SPRITE_W = 160
SPRITE_H = constants.GROUND_Y - 100

# Beacon Position
BEACON = (480, 160)
BEACON_COLOR = (255, 230, 120)

_sprite = None
_raw_sprite = None
_tile_cache = {}

_CLOUD_Y_RANGE = (30, 250)
_CLOUD_ALPHA_DAY = 55
_CLOUD_ALPHA_NIGHT = 80
_NUM_CLOUDS = 8
_SPAWN_X_OFFSCREEN = 1200

_clouds = []
_cloud_t = 0.0

_is_night = False


def _make_cloud(x: float | None = None) -> dict:
    y = random.uniform(*_CLOUD_Y_RANGE)
    speed = random.uniform(8, 20)
    sc = random.uniform(0.7, 1.4)
    
    puffs = [(0, 0, int(38 * sc), int(22 * sc))]
    n_extra = random.randint(2, 4)
    for _ in range(n_extra):
        dx = random.randint(-30, 30)
        dy = random.randint(-10, 8)
        rx = random.randint(14, 26)
        ry = random.randint(10, 18)
        puffs.append((int(dx * sc), int(dy * sc), int(rx * sc), int(ry * sc)))
    
    if x is None:
        x = random.uniform(-200, _SPAWN_X_OFFSCREEN)
    
    return {"x": x, "y": y, "speed": speed, "puffs": puffs, "alpha": 0, "scale": sc}


def _init_clouds():
    global _clouds, _cloud_t
    _cloud_t = 0.0
    _clouds  = [_make_cloud() for _ in range(_NUM_CLOUDS)]


def update_clouds(dt: float, night: bool = False):
    global _cloud_t, _clouds, _is_night
    _cloud_t += dt
    _is_night = night
    target_alpha = _CLOUD_ALPHA_NIGHT if night else _CLOUD_ALPHA_DAY
    
    for c in _clouds:
        c["x"] -= c["speed"] * dt
        
        if c["alpha"] < target_alpha:
            c["alpha"] = min(target_alpha, c["alpha"] + 60 * dt)
        elif c["alpha"] > target_alpha:
            c["alpha"] = max(target_alpha, c["alpha"] - 60 * dt)
        
        if c["x"] < -300:
            new = _make_cloud(_SPAWN_X_OFFSCREEN + random.uniform(0, 400))
            new["alpha"] = 0
            c.update(new)


def draw_clouds(screen: pygame.Surface, night: bool = False):
    if not _clouds:
        return
    
    if night:
        base_col = (120, 130, 160)
    else:
        base_col = (220, 225, 235)
    
    for c in _clouds:
        alpha = int(c["alpha"])
        if alpha <= 0:
            continue
            
        xs = [dx - rx for dx, dy, rx, ry in c["puffs"]] + [dx + rx for dx, dy, rx, ry in c["puffs"]]
        ys = [dy - ry for dx, dy, rx, ry in c["puffs"]] + [dy + ry for dx, dy, rx, ry in c["puffs"]]
        w  = (max(xs) - min(xs) + 2)
        h  = (max(ys) - min(ys) + 2)
        ox = -min(xs) + 1
        oy = -min(ys) + 1
        
        surf = pygame.Surface((view.scale(w), view.scale(h)), pygame.SRCALPHA)
        
        for dx, dy, rx, ry in c["puffs"]:
            cx_px = view.scale(ox + dx)
            cy_px = view.scale(oy + dy)
            rx_px = view.scale(rx)
            ry_px = view.scale(ry)
            pygame.draw.ellipse(surf, (*base_col, alpha),
                                (cx_px - rx_px, cy_px - ry_px, rx_px * 2, ry_px * 2))
        
        # Gentle vertical bob
        bob = math.sin(_cloud_t * 0.4 + c["y"]) * view.scale(2)
        
        screen_x = view.x(c["x"]) - view.scale(ox)
        screen_y = view.y(c["y"]) - view.scale(oy) + int(bob)
        screen.blit(surf, (screen_x, screen_y))


def init():
    global tmx_bg, _raw_sprite
    tmx_bg = pytmx.load_pygame("assets/map/bg/untitled.tmx")

    try:
        _raw_sprite = pygame.image.load("assets/sprites/lighthouse.webp").convert_alpha()
    except FileNotFoundError:
        _raw_sprite = None

    rebuild_scaled()
    _init_clouds()


def rebuild_scaled():
    global _sprite, _tile_cache
    _tile_cache = {}
    if _raw_sprite is None:
        _sprite = None
        return
    _sprite = pygame.transform.scale(
        _raw_sprite,
        (view.scale(SPRITE_W), view.scale(SPRITE_H))
    )


def draw(screen, night: bool = False):
    # Clouds sit in the sky, behind the lighthouse sprite
    draw_clouds(screen, night=night)
    
    if _sprite:
        pos = view.point(player.world_x(SPRITE_X), SPRITE_Y)
        screen.blit(_sprite, pos)
    
    draw_tmx(screen, tmx_bg)


def beacon_center():
    return view.point(player.world_x(BEACON[0]), BEACON[1])


def draw_beacon(screen, pulse=0.0, *, glow_radius, glow_pulse=0, glow_alpha=12, glow_alpha_pulse=20, core_radius=30, core_pulse=4, inner_glow_radius=None, inner_glow_ratio=0.85, inner_glow_alpha=20, inner_glow_alpha_pulse=25):
    cx, cy = beacon_center()
    
    # Calculate radii for the layered light blobs
    atmos_radius_px = view.scale(int(glow_radius * 2.8) + int(glow_pulse * pulse))
    atmos_sec_radius_px = view.scale(int(glow_radius * 1.9) + int(glow_pulse * pulse))
    glow_radius_px = view.scale(int(glow_radius * 1.3) + int(glow_pulse * pulse))
    
    # Prepare a transparent surface sized to the largest radius
    light_surf = pygame.Surface((atmos_radius_px * 2, atmos_radius_px * 2), pygame.SRCALPHA)
    center = (atmos_radius_px, atmos_radius_px)
    
    # Layer 1: Atmospheric Fringe (Outermost)
    fringe_alpha = 3 + int(5 * pulse)
    pygame.draw.circle(light_surf, (*BEACON_COLOR, fringe_alpha), center, atmos_radius_px)
    
    # Layer 2: Secondary Halo (Middle-outer)
    halo_alpha = 8 + int(10 * pulse)
    pygame.draw.circle(light_surf, (*BEACON_COLOR, halo_alpha), center, atmos_sec_radius_px)
    
    # Layer 3: Standard Glow (Main light body)
    standard_alpha = glow_alpha + int(glow_alpha_pulse * pulse)
    pygame.draw.circle(light_surf, (*BEACON_COLOR, standard_alpha), center, glow_radius_px)
    
    # Layer 4: Central Core (Smallest and brightest)
    core_alpha = 180 + int(75 * pulse)
    core_radius_px = view.scale(core_radius + int(core_pulse * pulse))
    pygame.draw.circle(light_surf, (*BEACON_COLOR, core_alpha), center, core_radius_px)
    
    # Blit the assembled light surface to the screen
    screen.blit(light_surf, (cx - atmos_radius_px, cy - atmos_radius_px))


def _rect(x_pos, y_pos, width, height):
    # Convert world-space dimensions and position to screen-space rect
    return view.rect(player.world_x(x_pos), y_pos, width, height)


def draw_tmx(screen, tmx):
    # Render all visible layers from the Tiled map
    tile_size = (view.scale(tmx.tilewidth * 2), view.scale(tmx.tileheight * 2))
    for layer in tmx.visible_layers:
        if hasattr(layer, "data"):
            for x, y, gid in layer:
                if gid == 0: continue
                
                tile = tmx.get_tile_image_by_gid(gid)
                if tile is None: continue
                
                # Scale tile and calculate position with world offset
                scaled_tile = _tile_cache.get((gid, tile_size))
                if scaled_tile is None:
                    scaled_tile = pygame.transform.scale(tile, tile_size)
                    _tile_cache[(gid, tile_size)] = scaled_tile
                render_pos = view.point(x * tmx.tilewidth * 1.2 - 300 + player._world_offset, y * tmx.tileheight * 1.2 - 120)
                
                screen.blit(scaled_tile, render_pos)
