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


def draw(screen):
    if _sprite:
        pos = view.point(player.world_x(SPRITE_X), SPRITE_Y)
        screen.blit(_sprite, pos)

    draw_tmx(screen, tmx_bg)


def beacon_center():
    # returns the screen pixel position of the beacon light
    return view.point(player.world_x(BEACON[0]), BEACON[1])


def draw_beacon(screen, pulse=0.0, *, glow_radius, glow_pulse=0, glow_alpha=12, glow_alpha_pulse=20, core_radius=30, core_pulse=4, inner_glow_radius=None, inner_glow_ratio=0.85, inner_glow_alpha=20, inner_glow_alpha_pulse=25):
    # Determine the screen-space center for the beacon
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