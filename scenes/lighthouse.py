import math
import random
import pygame
import entities.player as player
import constants
import core.view as view
import core.sound as sound
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

_CLOUD_Y_RANGE = (30, 250)
_CLOUD_ALPHA_DAY = 55
_CLOUD_ALPHA_NIGHT = 80
_NUM_CLOUDS = 8
_SPAWN_X_OFFSCREEN = 1200

_clouds = []
_cloud_t = 0.0

_is_night = False

_ocean_t = 0.0

_OCEAN_Y      = constants.GROUND_Y + 2
_OCEAN_HEIGHT = 200
_NUM_WAVE_STRIPS = 6

_WAVE_STRIPS = [
    dict(phase=0.0,   amp=5,  y_off=0,  a_day=160, a_night=100,
         col_day=(60, 100, 150), col_night=(30, 45, 80)),
    dict(phase=1.1,   amp=4,  y_off=12, a_day=130, a_night=80,
         col_day=(50, 88, 138), col_night=(25, 38, 70)),
    dict(phase=2.3,   amp=3,  y_off=24, a_day=105, a_night=65,
         col_day=(42, 76, 124), col_night=(20, 32, 62)),
    dict(phase=3.7,   amp=2,  y_off=38, a_day=85,  a_night=50,
         col_day=(34, 64, 108), col_night=(16, 26, 52)),
]

_foam: list[dict] = []
_FOAM_COUNT = 18

def _make_foam(i: int) -> dict:
    return {
        "wx":    random.uniform(-300, 700),
        "phase": random.uniform(0, math.tau),
        "speed": random.uniform(0.6, 1.4),
        "alpha": random.randint(60, 180),
        "size":  random.randint(1, 3),
        "strip": random.randint(0, 1),
    }


def _init_ocean():
    global _ocean_t, _foam
    _ocean_t = 0.0
    _foam = [_make_foam(i) for i in range(_FOAM_COUNT)]


def update_ocean(dt: float):
    global _ocean_t
    _ocean_t += dt
    for f in _foam:
        f["phase"] += dt * f["speed"]
        if f["phase"] > math.tau * 6:
            f["phase"] = 0.0
            f["wx"] = random.uniform(-300, 700)


def draw_ocean(screen: pygame.Surface, night: bool = False):
    sw, sh = screen.get_size()
    base_screen_y = view.y(_OCEAN_Y)
    ocean_h_px = view.scale(_OCEAN_HEIGHT)
    
    # number of x sample points for the wave polygon
    STEPS = 32
    step_px = sw // STEPS
    
    for strip in _WAVE_STRIPS:
        y_off_px  = view.scale(strip["y_off"])
        amp_px    = view.scale(strip["amp"])
        strip_y   = base_screen_y + y_off_px
        bottom_y  = base_screen_y + ocean_h_px + view.scale(4)
        
        col   = strip["col_night"]   if night else strip["col_day"]
        alpha = strip["a_night"]     if night else strip["a_day"]
        
        pts_top = []
        for i in range(STEPS + 1):
            px = i * step_px
            # world-x for this screen pixel
            wx = view.un_x(px) - player._world_offset
            wave_y = strip_y + int(amp_px * math.sin(
                wx * 0.025 + _ocean_t * 1.4 + strip["phase"]
            ))
            pts_top.append((px, wave_y))
        
        pts = pts_top + [(sw, bottom_y), (0, bottom_y)]
        
        surf = pygame.Surface((sw, sh), pygame.SRCALPHA)
        pygame.draw.polygon(surf, (*col, alpha), pts)
        screen.blit(surf, (0, 0))
    
    for f in _foam:
        strip = _WAVE_STRIPS[f["strip"]]
        y_off_px = view.scale(strip["y_off"])
        amp_px   = view.scale(strip["amp"])
        strip_y  = base_screen_y + y_off_px
        sx = view.x(f["wx"])
        if sx < -10 or sx > sw + 10:
            continue
        wx = f["wx"]
        wy = strip_y + int(amp_px * math.sin(
            wx * 0.025 + _ocean_t * 1.4 + strip["phase"]
        ))
        foam_y = wy - view.scale(f["size"])
        foam_alpha = int(f["alpha"] * (0.5 + 0.5 * math.sin(f["phase"] * 2)))
        foam_col = (220, 235, 255, foam_alpha) if not night else (160, 175, 210, foam_alpha // 2)
        sz = view.scale(f["size"])
        foam_surf = pygame.Surface((sz * 2 + 2, sz * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(foam_surf, foam_col, (sz + 1, sz + 1), sz)
        screen.blit(foam_surf, (int(sx) - sz, int(foam_y) - sz))




_rain_particles: list[dict] = []
_rain_t = 0.0
_rain_seeded_day = -1   # tracks which day we last seeded rain for

_RAIN_CFG = {
    #  count  angle_deg  speed   len  alpha_range       color
    4:  dict(n=40,   ang=-78,  spd=320,  ln=8,  ar=(40,  90),  col=(160, 175, 200)),
    7:  dict(n=90,   ang=-75,  spd=480,  ln=14, ar=(60,  130), col=(140, 160, 195)),
    8:  dict(n=140,  ang=-68,  spd=600,  ln=18, ar=(70,  150), col=(120, 140, 185)),
    9:  dict(n=190,  ang=-62,  spd=700,  ln=22, ar=(80,  165), col=(110, 130, 180)),
    10: dict(n=250,  ang=-55,  spd=820,  ln=26, ar=(90,  180), col=(140, 80,  90)),
}


def _make_rain_particle(cfg: dict, screen_w: int, screen_h: int) -> dict:
    return {
        "x":     random.uniform(0, screen_w),
        "y":     random.uniform(-screen_h, 0),       # start above viewport
        "alpha": random.randint(*cfg["ar"]),
        "len":   random.uniform(cfg["ln"] * 0.7, cfg["ln"] * 1.3),
        "speed": random.uniform(cfg["spd"] * 0.85, cfg["spd"] * 1.15),
    }


def _init_rain(day: int, screen_w: int, screen_h: int):
    global _rain_particles, _rain_t
    _rain_t = 0.0
    cfg = _RAIN_CFG.get(day)
    if cfg is None:
        _rain_particles = []
        return
    _rain_particles = [_make_rain_particle(cfg, screen_w, screen_h)
                       for _ in range(cfg["n"])]


def update_rain(dt: float, day: int, screen_w: int, screen_h: int):
    global _rain_t
    _rain_t += dt
    cfg = _RAIN_CFG.get(day)
    if not cfg or not _rain_particles:
        return
    
    ang_rad = math.radians(cfg["ang"])
    vx = math.cos(ang_rad) * cfg["spd"]
    vy = -math.sin(ang_rad) * cfg["spd"]
    
    for p in _rain_particles:
        p["x"] += vx * dt
        p["y"] += vy * dt
        # recycle when off-screen bottom or right
        if p["y"] > screen_h + 20 or p["x"] > screen_w + 20 or p["x"] < -20:
            p.update(_make_rain_particle(cfg, screen_w, screen_h))
            p["y"] = random.uniform(-screen_h * 0.5, 0)


def draw_rain(screen: pygame.Surface, day: int, night: bool = False):
    cfg = _RAIN_CFG.get(day)
    if not cfg or not _rain_particles:
        return
    
    ang_rad = math.radians(cfg["ang"])
    dx = math.cos(ang_rad)
    dy = -math.sin(ang_rad)
    
    r, g, b = cfg["col"]
    if night:
        r = max(0, r - 30)
        g = max(0, g - 20)
        b = max(0, b - 10)
    
    rain_surf = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    
    for p in _rain_particles:
        length = view.scale(p["len"])
        x1 = int(p["x"])
        y1 = int(p["y"])
        x2 = int(p["x"] + dx * length)
        y2 = int(p["y"] + dy * length)
        pygame.draw.line(rain_surf, (r, g, b, p["alpha"]), (x1, y1), (x2, y2),
                         max(1, view.scale(1)))
    
    screen.blit(rain_surf, (0, 0))


def _get_current_day() -> int:
    try:
        import core.day_cycle as day_cycle
        return day_cycle.day
    except Exception:
        return 1


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
    global _cloud_t, _clouds, _is_night, _rain_seeded_day
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
        
    update_ocean(dt)
    
    current_day = _get_current_day()
    if sound.is_rain_day(current_day):
        sw, sh = pygame.display.get_surface().get_size()
        if _rain_seeded_day != current_day:
            _init_rain(current_day, sw, sh)
            _rain_seeded_day = current_day
        update_rain(dt, current_day, sw, sh)
    else:
        _rain_seeded_day = -1


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
    global tmx_bg, _sprite
    tmx_bg = pytmx.load_pygame("assets/map/bg/untitled.tmx")

    try:
        raw_image = pygame.image.load("assets/sprites/lighthouse.webp").convert_alpha()
        _sprite = pygame.transform.scale(
            raw_image, (view.scale(SPRITE_W), view.scale(SPRITE_H))
        )
    except FileNotFoundError:
        _sprite = None

    _init_clouds()
    _init_ocean()

    # Rain is initialised in update_clouds once we know the screen size;
    # seed it here with a dummy size, it will be re-seeded on first update.
    _init_rain(1, 1280, 720)


def draw(screen, night: bool = False):
    # Clouds sit in the sky, behind the lighthouse sprite
    draw_clouds(screen, night=night)
    draw_ocean(screen, night=night)
    
    if _sprite:
        pos = view.point(player.world_x(SPRITE_X), SPRITE_Y)
        screen.blit(_sprite, pos)
    
    draw_tmx(screen, tmx_bg)

    if sound.is_rain_day(_get_current_day()):
        draw_rain(screen, _get_current_day(), night=night)


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
    for layer in tmx.visible_layers:
        if hasattr(layer, "data"):
            for x, y, gid in layer:
                if gid == 0: continue
                
                tile = tmx.get_tile_image_by_gid(gid)
                if tile is None: continue
                
                # Scale tile and calculate position with world offset
                scaled_tile = pygame.transform.scale(tile, (int(tmx.tilewidth * 2), int(tmx.tileheight * 2)))
                render_pos = view.point(x * tmx.tilewidth * 1.2 - 300 + player._world_offset, y * tmx.tileheight * 1.2 - 120)
                
                screen.blit(scaled_tile, render_pos)