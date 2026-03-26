import pygame
import entities.player as player
import constants
import core.view as view

import pytmx

# world space positions for the background elements
GROUND          = (-250, constants.GROUND_Y, view.BASE_W, 140)
TOWER           = (430, 120, 100, constants.GROUND_Y - 120)
LANTERN         = (420, 100, 120, 40)
BEACON          = (480, 200)
BEACON_COLOR    = (255, 230, 120)


def init():
    global tmx_bg
    # load the tiled map file that contains the background tiles
    tmx_bg = pytmx.load_pygame("assets/map/bg/untitled.tmx")


def _rect(x_pos, y_pos, width, height):
    # converts world coordinates to screen coordinates using the scroll offset
    return view.rect(player.world_x(x_pos), y_pos, width, height)


def draw_tmx(screen, tmx):
    for layer in tmx.visible_layers:
        if hasattr(layer, "data"):
            for x, y, gid in layer:
                # gid 0 means empty tile, skip it
                if gid == 0:
                    continue    
                tile = tmx.get_tile_image_by_gid(gid)
                if tile is None:
                    continue    
                # scale the tile up to match the zoom level
                scaled_tile = pygame.transform.scale(tile, (int(tmx.tilewidth * 2), int(tmx.tileheight * 2)))
                # position the tile using the scroll offset so it moves with the world
                screen.blit(scaled_tile, view.point(
                    x * tmx.tilewidth * 1.2 - 300 + player._world_offset,
                    y * tmx.tileheight * 1.2 - 120
                ))    

def draw(screen):
    # ground rect is commented out because the tilemap covers it visually
    # pygame.draw.rect(screen, (55, 50, 70), _rect(*GROUND))
    pygame.draw.rect(screen, (200, 195, 185), _rect(*TOWER))
    pygame.draw.rect(screen, (240, 220, 130), _rect(*LANTERN))
    
    draw_tmx(screen, tmx_bg)


def beacon_center():
    # returns the screen pixel position of the beacon light
    return view.point(player.world_x(BEACON[0]), BEACON[1])


def draw_beacon(
    screen,
    pulse=0.0,
    *,
    glow_radius,
    glow_pulse=0,
    glow_alpha=18,
    glow_alpha_pulse=0,
    core_radius=40,
    core_pulse=0,
    inner_glow_radius=None,
    inner_glow_ratio=0.72,
    inner_glow_alpha=None,
    inner_glow_alpha_pulse=0,
):
    # pulse is a 0.0 to 1.0 value that drives the breathing animation
    cx, cy = beacon_center()

    # outer glow drawn on a transparent surface so its alpha blends properly
    glow_radius_px = view.scale(glow_radius + int(glow_pulse * pulse))
    glow = pygame.Surface((glow_radius_px * 2, glow_radius_px * 2), pygame.SRCALPHA)

    pygame.draw.circle(
        glow,
        (*BEACON_COLOR, glow_alpha + int(glow_alpha_pulse * pulse)),
        (glow_radius_px, glow_radius_px),
        glow_radius_px,
    )

    # optional inner glow ring drawn on the same surface before blitting
    if inner_glow_alpha is not None:
        inner_radius_px = max(view.scale(inner_glow_radius or 0), int(glow_radius_px * inner_glow_ratio))
        pygame.draw.circle(
            glow,
            (*BEACON_COLOR, inner_glow_alpha + int(inner_glow_alpha_pulse * pulse)),
            (glow_radius_px, glow_radius_px),
            inner_radius_px,
        )

    screen.blit(glow, (cx - glow_radius_px, cy - glow_radius_px))
    # solid filled circle drawn on top as the bright core of the beacon
    pygame.draw.circle(screen, BEACON_COLOR, (cx, cy), view.scale(core_radius + int(core_pulse * pulse)))
