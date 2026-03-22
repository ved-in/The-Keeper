import pygame
import core.player as player
import constants
import core.view as view

import pytmx

GROUND          = (-250, constants.GROUND_Y, view.BASE_W, 140)
TOWER           = (430, 120, 100, constants.GROUND_Y - 120)
LANTERN         = (420, 100, 120, 40)
BEACON          = (480, 200)
BEACON_COLOR    = (255, 230, 120)


def init():
    global tmx_bg
    tmx_bg = pytmx.load_pygame("assets/map/bg/untitled.tmx")


def _rect(x_pos, y_pos, width, height):
    return view.rect(player.world_x(x_pos), y_pos, width, height)

def draw_tmx(screen, tmx):
    for layer in tmx.visible_layers:
        if hasattr(layer, "data"):
            for x, y, gid in layer:
                if gid == 0:
                    continue    
                tile = tmx.get_tile_image_by_gid(gid)
                if tile is None:
                    continue    
                scaled_tile = pygame.transform.scale(tile, (int(tmx.tilewidth * 2), int(tmx.tileheight * 2)))
                screen.blit(scaled_tile, view.point(
                    x * tmx.tilewidth * 1.2 - 300 + player._world_offset,
                    y * tmx.tileheight * 1.2 - 120
                ))    

def draw(screen):
    #pygame.draw.rect(screen, (55, 50, 70), _rect(*GROUND))
    # Hidden cuz now we have ground
    pygame.draw.rect(screen, (200, 195, 185), _rect(*TOWER))
    pygame.draw.rect(screen, (240, 220, 130), _rect(*LANTERN))
    
    draw_tmx(screen, tmx_bg)


def beacon_center():
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
    cx, cy = beacon_center()
    glow_radius_px = view.scale(glow_radius + int(glow_pulse * pulse))
    glow = pygame.Surface((glow_radius_px * 2, glow_radius_px * 2), pygame.SRCALPHA)

    pygame.draw.circle(
        glow,
        (*BEACON_COLOR, glow_alpha + int(glow_alpha_pulse * pulse)),
        (glow_radius_px, glow_radius_px),
        glow_radius_px,
    )

    if inner_glow_alpha is not None:
        inner_radius_px = max(view.scale(inner_glow_radius or 0), int(glow_radius_px * inner_glow_ratio))
        pygame.draw.circle(
            glow,
            (*BEACON_COLOR, inner_glow_alpha + int(inner_glow_alpha_pulse * pulse)),
            (glow_radius_px, glow_radius_px),
            inner_radius_px,
        )

    screen.blit(glow, (cx - glow_radius_px, cy - glow_radius_px))
    pygame.draw.circle(screen, BEACON_COLOR, (cx, cy), view.scale(core_radius + int(core_pulse * pulse)))
