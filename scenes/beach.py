"""
Beach scene.

Only active on days defined in constants.BEACH_DAYS (currently Day 5).
The scientist has sensor cases that need to be deployed at marked spots.
"""

import math

import pygame

import constants
import core.day_cycle as day_cycle
import core.view as view
import entities.animations as animations
import systems.tasks as tasks
import systems.neglect as neglect
import ui.dialogue as dialogue
import ui.hud as hud

_CRATE_SPOTS = [
    {"x": 220, "y": 352, "w": 42, "h": 30},
    {"x": 400, "y": 366, "w": 42, "h": 30},
    {"x": 560, "y": 348, "w": 42, "h": 30},
    {"x": 650, "y": 364, "w": 42, "h": 30},
]

_SKY_TOP = (82, 62, 86)
_SKY_HORIZON = (204, 152, 118)
_WATER_DARK = (44, 68, 98)
_WATER_MID = (58, 96, 128)
_WATER_LIGHT = (78, 124, 150)
_SAND_DRY = (188, 166, 126)
_SAND_WET = (138, 118, 92)
_FOAM = (218, 204, 176)

_SCIENTIST_KEY = "beach_scientist"
_SCIENTIST_FEET = (112, 360)
_HUT_STAIR_BOTTOM_PX = 83
_HUT_SOURCE_H = 122
_HUT_SAND_X = 730
_HUT_STAIR_Y = 390

_crates_placed: list[bool] = []
_carrying: bool = False
_font = None
_task_idx: int = 0
_crates_day: int = -1

_raw_assets: dict[str, pygame.Surface] = {}
_scaled_assets: dict[str, pygame.Surface] = {}
_scaled_for: float | None = None
_scientist_registered = False


def init() -> None:
    global _crates_placed, _carrying, _font, _task_idx, _crates_day
    _font = view.font(9, constants.FONT_PATH)
    _carrying = False
    _task_idx = 0

    _ensure_assets()
    _ensure_scientist_animation()

    for task in tasks.get_day_tasks(day_cycle.day):
        if task.get("task_type") == "beach":
            _task_idx = task.get("idx", 0)
            break

    if _crates_day != day_cycle.day:
        _crates_placed = [False] * len(_CRATE_SPOTS)
        _crates_day = day_cycle.day


def handle_event(event: pygame.event.Event) -> None:
    global _carrying

    if event.type == pygame.KEYDOWN and event.key in constants.ADVANCE_KEYS:
        dialogue.advance()

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        if not dialogue.active():
            _handle_click(event.pos)


def _handle_click(pos) -> None:
    global _carrying

    if not _carrying:
        pile = _crate_pile_rect()
        if pile.collidepoint(pos) and not all(_crates_placed):
            _carrying = True
            dialogue.show(["You pick up a sensor case."], style="thought", default_speaker="player")
            return

    if _carrying:
        for i, spot in enumerate(_CRATE_SPOTS):
            if _crates_placed[i]:
                continue
            if _spot_rect(spot).collidepoint(pos):
                _crates_placed[i] = True
                _carrying = False
                dialogue.show(["Sensor placed."], style="thought", default_speaker="player")
                if all(_crates_placed):
                    import scenes.day as day_scene

                    day_scene.notify_task_done(_task_idx)
                    dialogue.show(
                        ["All sensors placed.", "The scientist gives a curt nod."],
                        style="thought",
                        default_speaker="player",
                    )
                return

    if _scientist_rect().collidepoint(pos):
        lines = constants.VISITORS[0]["lines"].get(
            day_cycle.day,
            constants.VISITORS[0]["lines"].get("default", ["..."]),
        )
        dialogue.show(lines, reveal_speed=40)
        return

    if _back_rect().collidepoint(pos):
        import core.game as game

        game.switch("lighthouse")


def update(dt: float) -> None:
    dialogue.update(dt)
    animations.update(dt)
    if dialogue.active() or all(_crates_placed):
        return
    rate = constants.NEGLECT_BEACH_CARRY_RATE if _carrying else constants.NEGLECT_BEACH_IDLE_RATE
    neglect.add(
        dt * rate,
        "You lose too much time on the beach while the lighthouse waits.",
    )


def draw(screen: pygame.Surface) -> None:
    cr = view.content_rect()
    _ensure_scaled_assets()

    _draw_sky(screen, cr)
    _draw_water(screen, cr)
    _draw_horizon_set(screen)
    _draw_sand(screen, cr)
    _draw_beach_hut(screen)
    _draw_sensor_sites(screen)
    _draw_cargo_area(screen)
    _draw_scientist(screen)

    if _carrying:
        _draw_carrying_indicator(screen)


def draw_ui(screen: pygame.Surface) -> None:
    hud.draw(screen)
    _draw_back_button(screen)
    dialogue.draw(screen)
    if not dialogue.active() and not all(_crates_placed):
        if not _carrying:
            lines = [
                "Pick up a sensor case from the stack.",
                "Then place it on one of the marked deployment pads.",
            ]
        else:
            lines = [
                "You are carrying a sensor case.",
                "Click a marked pad to deploy it in the sand.",
            ]
        hud.draw_help_card(screen, "Beach Task", lines, accent=(112, 166, 178))


def _draw_sky(screen: pygame.Surface, cr: pygame.Rect) -> None:
    for i in range(cr.height):
        t = i / max(1, cr.height - 1)
        color = _mix(_SKY_TOP, _SKY_HORIZON, min(1.0, t * 1.15))
        pygame.draw.line(screen, color, (cr.left, cr.top + i), (cr.right, cr.top + i))

    overlay = pygame.Surface(cr.size, pygame.SRCALPHA)
    pygame.draw.circle(
        overlay,
        (244, 192, 124, 40),
        (view.scale(720), view.scale(150)),
        view.scale(120),
    )
    pygame.draw.circle(
        overlay,
        (255, 218, 162, 65),
        (view.scale(720), view.scale(150)),
        view.scale(62),
    )
    pygame.draw.ellipse(
        overlay,
        (36, 22, 40, 40),
        pygame.Rect(view.scale(80), view.scale(70), view.scale(340), view.scale(84)),
    )
    pygame.draw.ellipse(
        overlay,
        (58, 32, 48, 34),
        pygame.Rect(view.scale(540), view.scale(40), view.scale(250), view.scale(62)),
    )
    screen.blit(overlay, cr.topleft)


def _draw_water(screen: pygame.Surface, cr: pygame.Rect) -> None:
    water = pygame.Rect(cr.left, view.y(180), cr.width, view.scale(132))

    horizon_blend = _mix(_SKY_HORIZON, _WATER_MID, 0.55)
    for i in range(water.height):
        t = i / max(1, water.height - 1)
        color = _mix(horizon_blend, _WATER_DARK, min(1.0, t))
        pygame.draw.line(screen, color, (water.left, water.top + i), (water.right, water.top + i))

    t_ms = pygame.time.get_ticks()
    wave_surf = pygame.Surface((water.width, water.height), pygame.SRCALPHA)

    num_rows = 16
    for w in range(num_rows):
        y_frac = (w + 0.5) / num_rows
        y_base = int(water.height * y_frac)

        amplitude = view.scale(0.4 + y_frac * 4.5)
        alpha = int(18 + 72 * (y_frac ** 0.7))
        wave_col = (*_WATER_LIGHT, alpha)

        freq1 = 0.026 - y_frac * 0.012
        freq2 = 0.048 - y_frac * 0.020
        speed = 0.0018 + y_frac * 0.0010

        step = max(2, int(view.scale(2 + y_frac * 3)))
        points = []
        for x in range(0, water.width + step, step):
            wy = y_base + int(
                math.sin(x * freq1 + t_ms * speed + w * 1.0) * amplitude
                + math.sin(x * freq2 + t_ms * speed * 1.5 + w * 0.7) * (amplitude * 0.38)
            )
            points.append((x, max(0, min(water.height - 1, wy))))
        if len(points) >= 2:
            pygame.draw.lines(wave_surf, wave_col, False, points, max(1, view.scale(1)))

    screen.blit(wave_surf, water.topleft)

    # Soft sun-path glow (no vertical line artifacts)
    sun_cx = view.x(720)
    refl_w = view.scale(260)
    refl_h = view.scale(22)
    refl_surf = pygame.Surface((refl_w, refl_h), pygame.SRCALPHA)
    pulse = 0.55 + 0.45 * abs(math.sin(t_ms * 0.0018))
    for i in range(refl_h):
        t_row = i / max(1, refl_h - 1)
        row_fade = math.sin(t_row * math.pi)
        a = int(38 * pulse * row_fade)
        pygame.draw.line(refl_surf, (255, 210, 150, a), (0, i), (refl_w, i))
    refl_x = sun_cx - refl_w // 2
    if refl_x + refl_w > water.left and refl_x < water.right:
        clip_x = max(0, water.left - refl_x)
        clip_w = min(refl_w - clip_x, water.right - max(water.left, refl_x))
        if clip_w > 0:
            screen.blit(refl_surf, (max(water.left, refl_x), water.top + view.scale(4)),
                        pygame.Rect(clip_x, 0, clip_w, refl_h))

    # Atmospheric haze at horizon
    haze_h = view.scale(14)
    haze = pygame.Surface((water.width, haze_h), pygame.SRCALPHA)
    for i in range(haze_h):
        a = int(70 * (1.0 - i / max(1, haze_h)))
        pygame.draw.line(haze, (160, 138, 158, a), (0, i), (water.width, i))
    screen.blit(haze, water.topleft)

    # Shore foam
    foam_y2 = water.bottom - view.scale(3)
    for x in range(cr.left, cr.right, view.scale(32)):
        h = view.scale(3) + int(math.sin((x / max(1, view.scale(18))) + t_ms * 0.004) * view.scale(1))
        pygame.draw.line(screen, _FOAM, (x, foam_y2), (x + view.scale(18), foam_y2 + h), max(1, view.scale(1)))


def _draw_horizon_set(screen: pygame.Surface) -> None:
    boat = _scaled_assets["boat_mid"]

    boat_bob = int(math.sin(pygame.time.get_ticks() * 0.0022) * view.scale(1))
    boat_y = view.y(222) - boat.get_height() + boat_bob
    boat_pos = (view.x(515), boat_y)

    shadow = pygame.Surface((boat.get_width() + view.scale(8), view.scale(5)), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (22, 32, 48, 55), shadow.get_rect())
    screen.blit(shadow, (boat_pos[0] - view.scale(4), boat_pos[1] + boat.get_height()))
    screen.blit(boat, boat_pos)


def _sand_color_at_y(y_coord: int) -> tuple:
    """Return the exact sand gradient color at a given base y coordinate."""
    sand_top = 300
    sand_bottom = 540  # base canvas height
    t = (y_coord - sand_top) / max(1, sand_bottom - sand_top)
    return _mix(_SAND_WET, _SAND_DRY, min(1.0, t * 1.35))


def _draw_beach_hut(screen: pygame.Surface) -> None:
    hut = _scaled_assets["hut"]
    barrel_big = _scaled_assets["barrel_big"]
    barrel_small = _scaled_assets["barrel_small"]
    case_small = _scaled_assets["sensor_case_small"]

    # Pixel in the scaled sprite where the stair base meets the ground
    stair_bottom = int(round(hut.get_height() * (_HUT_STAIR_BOTTOM_PX / _HUT_SOURCE_H)))
    hut_x = view.x(_HUT_SAND_X)
    hut_y = view.y(_HUT_STAIR_Y) - stair_bottom

    # Draw hut clipped to EXACTLY the stair bottom — no stilt pixels shown at all
    screen.blit(hut, (hut_x, hut_y), pygame.Rect(0, 0, hut.get_width(), stair_bottom))

    # --- Sand berm that buries the stilt bases and blends with the beach ---
    # The berm is two layers: a filled rect as a solid base (ensures full occlusion),
    # then a wider ellipse on top for the natural mound silhouette.
    berm_top_y = view.y(_HUT_STAIR_Y) - view.scale(6)

    # Solid rectangle base — same color as the sand at this exact y, so it's invisible
    # against the background and only covers the exposed stilt pixels.
    sand_col = _sand_color_at_y(_HUT_STAIR_Y)
    fill_rect = pygame.Rect(
        hut_x - view.scale(8),
        berm_top_y,
        hut.get_width() + view.scale(16),
        view.scale(30),
    )
    pygame.draw.rect(screen, sand_col, fill_rect)

    # Ellipse mound — slightly lighter (raised sand catches more light)
    mound_col = _mix(sand_col, _SAND_DRY, 0.35)
    mound_rect = pygame.Rect(
        hut_x - view.scale(24),
        berm_top_y - view.scale(4),
        hut.get_width() + view.scale(48),
        view.scale(38),
    )
    pygame.draw.ellipse(screen, mound_col, mound_rect)

    # Subtle highlight ridge on mound top
    highlight_col = _mix(mound_col, _SAND_DRY, 0.4)
    pygame.draw.ellipse(
        screen,
        highlight_col,
        pygame.Rect(
            mound_rect.x + view.scale(28),
            mound_rect.y + view.scale(4),
            mound_rect.width - view.scale(56),
            view.scale(14),
        ),
    )

    # Props sitting on the berm surface (drawn after berm so they appear on top)
    prop_y = berm_top_y + view.scale(6)
    prop_shadow = pygame.Surface((view.scale(110), view.scale(10)), pygame.SRCALPHA)
    pygame.draw.ellipse(prop_shadow, (44, 34, 24, 80), prop_shadow.get_rect())
    screen.blit(prop_shadow, (hut_x - view.scale(18), prop_y + view.scale(2)))

    screen.blit(barrel_big,   (hut_x - view.scale(22), prop_y - barrel_big.get_height()))
    screen.blit(case_small,   (hut_x + view.scale(8),  prop_y - case_small.get_height() + view.scale(4)))
    screen.blit(barrel_small, (hut_x + view.scale(42), prop_y - barrel_small.get_height() + view.scale(2)))


def _draw_sand(screen: pygame.Surface, cr: pygame.Rect) -> None:
    sand = pygame.Rect(cr.left, view.y(300), cr.width, cr.bottom - view.y(300))
    for i in range(sand.height):
        t = i / max(1, sand.height - 1)
        color = _mix(_SAND_WET, _SAND_DRY, min(1.0, t * 1.35))
        pygame.draw.line(screen, color, (sand.left, sand.top + i), (sand.right, sand.top + i))

    # Gentle dune ripples — kept subtle so they don't look cluttered
    for x in range(cr.left, cr.right, view.scale(140)):
        width = view.scale(70)
        dune_y = view.y(318 + ((x // max(1, view.scale(14))) % 3) * 4)
        dune = pygame.Rect(x, dune_y, width, view.scale(8))
        pygame.draw.ellipse(screen, (182, 164, 126), dune)

    # Small pebbles/rocks
    for x in range(cr.left + view.scale(50), cr.right - view.scale(200), view.scale(190)):
        rock = pygame.Rect(x, view.y(400 + (x // max(1, view.scale(28))) % 14), view.scale(12), view.scale(5))
        pygame.draw.ellipse(screen, (108, 94, 80), rock)


def _draw_sensor_sites(screen: pygame.Surface) -> None:
    mouse_pos = pygame.mouse.get_pos()
    sensor = _scaled_assets["sensor"]
    pulse = 0.5 + math.sin(pygame.time.get_ticks() * 0.006) * 0.5

    for i, spot in enumerate(_CRATE_SPOTS):
        rect = _spot_rect(spot)
        shadow = pygame.Rect(
            rect.centerx - view.scale(16),
            rect.bottom - view.scale(5),
            view.scale(32),
            view.scale(8),
        )
        pygame.draw.ellipse(screen, (52, 44, 36), shadow)

        if _crates_placed[i]:
            sensor_rect = sensor.get_rect(midbottom=(rect.centerx, rect.bottom + view.scale(2)))
            screen.blit(sensor, sensor_rect)
            light_color = (114, 208, 212) if pulse > 0.5 else (228, 190, 108)
            pygame.draw.circle(
                screen,
                light_color,
                (sensor_rect.centerx, sensor_rect.top + view.scale(7)),
                view.scale(2),
            )
            continue

        hovered = rect.collidepoint(mouse_pos)
        ring = pygame.Surface((rect.width + view.scale(18), rect.height + view.scale(12)), pygame.SRCALPHA)
        pygame.draw.ellipse(
            ring,
            (132, 186, 198, 90 if hovered or _carrying else 55),
            ring.get_rect(),
            width=max(1, view.scale(2)),
        )
        screen.blit(ring, (rect.centerx - ring.get_width() // 2, rect.centery - ring.get_height() // 2))

        pygame.draw.line(
            screen,
            (186, 214, 220),
            (rect.left + view.scale(6), rect.top + view.scale(5)),
            (rect.right - view.scale(6), rect.bottom - view.scale(5)),
            max(1, view.scale(2)),
        )
        pygame.draw.line(
            screen,
            (186, 214, 220),
            (rect.right - view.scale(6), rect.top + view.scale(5)),
            (rect.left + view.scale(6), rect.bottom - view.scale(5)),
            max(1, view.scale(2)),
        )


def _draw_cargo_area(screen: pygame.Surface) -> None:
    pile = _crate_pile_rect()
    mouse_pos = pygame.mouse.get_pos()
    hovered = pile.collidepoint(mouse_pos) and not all(_crates_placed)

    shadow = pygame.Surface((pile.width + view.scale(24), view.scale(16)), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (40, 30, 24, 110), shadow.get_rect())
    screen.blit(shadow, (pile.centerx - shadow.get_width() // 2, pile.bottom - view.scale(8)))

    remaining_cases = max(0, len(_CRATE_SPOTS) - sum(_crates_placed) - (1 if _carrying else 0))
    case_large = _scaled_assets["sensor_case"]
    case_small = _scaled_assets["sensor_case_small"]
    barrel_big = _scaled_assets["barrel_big"]
    barrel_small = _scaled_assets["barrel_small"]
    monitor = _scaled_assets["monitor"]

    base_x = pile.left + view.scale(8)
    base_y = pile.bottom - case_large.get_height() + view.scale(2)
    positions = [
        (base_x + view.scale(18), base_y - view.scale(18), case_large),
        (base_x, base_y, case_large),
        (base_x + view.scale(38), base_y + view.scale(2), case_large),
        (base_x + view.scale(58), base_y - view.scale(12), case_small),
    ]
    for x_pos, y_pos, surf in positions[:remaining_cases]:
        screen.blit(surf, (x_pos, y_pos))

    screen.blit(barrel_small, (pile.left - view.scale(6), pile.bottom - barrel_small.get_height()))
    screen.blit(barrel_big, (pile.right - barrel_big.get_width() + view.scale(12), pile.bottom - barrel_big.get_height() + view.scale(2)))
    screen.blit(monitor, (pile.left + view.scale(74), pile.top - monitor.get_height() + view.scale(10)))

    if hovered and not _carrying:
        _draw_label(screen, pile, "Pick Up Sensor Case", (224, 214, 188))
    elif remaining_cases > 0 and not _carrying:
        _draw_soft_outline(screen, pile, (132, 186, 198))


def _draw_scientist(screen: pygame.Surface) -> None:
    rect = _scientist_rect()
    frame = animations.get_frame(_SCIENTIST_KEY, "idle")
    hover = rect.collidepoint(pygame.mouse.get_pos())

    shadow = pygame.Surface((view.scale(42), view.scale(12)), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (40, 30, 24, 120), shadow.get_rect())
    screen.blit(shadow, (rect.centerx - shadow.get_width() // 2, rect.bottom - view.scale(7)))

    if frame:
        bob = int(math.sin(pygame.time.get_ticks() * 0.0035) * view.scale(1))
        frame_rect = frame.get_rect(midbottom=(view.x(_SCIENTIST_FEET[0]), view.y(_SCIENTIST_FEET[1]) + bob))
        screen.blit(frame, frame_rect)
    else:
        pygame.draw.rect(screen, (160, 140, 180), rect, border_radius=view.scale(3))

    if hover:
        _draw_label(screen, rect, "Scientist", (226, 220, 234))


def _draw_carrying_indicator(screen: pygame.Surface) -> None:
    case = _scaled_assets["sensor_case_small"]
    mx, my = pygame.mouse.get_pos()
    shadow = pygame.Surface((case.get_width(), view.scale(10)), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (24, 18, 14, 90), shadow.get_rect())
    screen.blit(shadow, (mx - case.get_width() // 2, my + view.scale(8)))

    carry = case.copy()
    carry.set_alpha(220)
    screen.blit(carry, (mx - case.get_width() // 2, my - case.get_height() // 2))


def _draw_back_button(screen: pygame.Surface) -> None:
    r = _back_rect()
    col = (50, 46, 66) if not r.collidepoint(pygame.mouse.get_pos()) else (70, 66, 90)
    pygame.draw.rect(screen, col, r, border_radius=view.scale(4))
    pygame.draw.rect(screen, (90, 86, 110), r, width=max(1, view.scale(1)), border_radius=view.scale(4))
    lbl = _font.render("<- Back", True, (200, 195, 215))
    screen.blit(lbl, (r.centerx - lbl.get_width() // 2, r.centery - lbl.get_height() // 2))


def _back_rect() -> pygame.Rect:
    return view.rect(10, 490, 60, 22)


def _spot_rect(spot: dict) -> pygame.Rect:
    return view.rect(spot["x"], spot["y"], spot["w"], spot["h"])


def _crate_pile_rect() -> pygame.Rect:
    return view.rect(162, 308, 118, 72)


def _scientist_rect() -> pygame.Rect:
    frame = animations.get_frame(_SCIENTIST_KEY, "idle")
    if frame:
        rect = frame.get_rect(midbottom=view.point(*_SCIENTIST_FEET))
        rect.inflate_ip(-view.scale(18), -view.scale(6))
        return rect
    return view.rect(92, 274, 54, 82)


def _ensure_assets() -> None:
    if _raw_assets:
        return

    _raw_assets["boat"] = _load_surface("assets/map/beach/Boat.png")
    _raw_assets["hut"] = _load_surface("assets/map/beach/Fishing_hut.png")
    _raw_assets["barrel_small"] = _load_surface("assets/map/beach/Fishbarrel2.png")
    _raw_assets["barrel_big"] = _load_surface("assets/map/beach/Fishbarrel4.png")
    _raw_assets["sensor_case"] = _build_sensor_case()
    _raw_assets["sensor"] = _build_sensor()
    _raw_assets["monitor"] = _build_monitor()


def _ensure_scaled_assets() -> None:
    global _scaled_assets, _scaled_for
    scale_now = view.current_scale()
    if _scaled_for == scale_now and _scaled_assets:
        return

    _scaled_for = scale_now
    _scaled_assets = {
        "boat": _scale_surface(_raw_assets["boat"], 158, 38),
        "boat_distant": _scale_surface(_raw_assets["boat"], 96, 24),
        "boat_mid": _scale_surface(_raw_assets["boat"], 116, 28),
        "hut": _scale_surface(_raw_assets["hut"], 270, 172),
        "barrel_small": _scale_surface(_raw_assets["barrel_small"], 34, 30),
        "barrel_big": _scale_surface(_raw_assets["barrel_big"], 40, 46),
        "sensor_case": _scale_surface(_raw_assets["sensor_case"], 56, 34),
        "sensor_case_small": _scale_surface(_raw_assets["sensor_case"], 44, 28),
        "sensor": _scale_surface(_raw_assets["sensor"], 24, 48),
        "monitor": _scale_surface(_raw_assets["monitor"], 34, 28),
    }


def _ensure_scientist_animation() -> None:
    global _scientist_registered
    if not _scientist_registered:
        animations.register(
            _SCIENTIST_KEY,
            "idle",
            constants.VISITORS[0]["anim_folder"],
            scale=4.1,
        )
        _scientist_registered = True
    animations.reset(_SCIENTIST_KEY)


def _scale_surface(surf: pygame.Surface, base_w: int, base_h: int) -> pygame.Surface:
    return pygame.transform.scale(surf, (view.scale(base_w), view.scale(base_h)))


def _load_surface(path: str) -> pygame.Surface:
    try:
        return pygame.image.load(path).convert_alpha()
    except (FileNotFoundError, pygame.error):
        return pygame.Surface((1, 1), pygame.SRCALPHA)


def _build_sensor_case() -> pygame.Surface:
    surf = pygame.Surface((48, 30), pygame.SRCALPHA)
    pygame.draw.rect(surf, (78, 74, 70), pygame.Rect(5, 6, 38, 20), border_radius=4)
    pygame.draw.rect(surf, (120, 116, 108), pygame.Rect(6, 7, 36, 18), border_radius=4)
    pygame.draw.rect(surf, (58, 50, 46), pygame.Rect(11, 10, 26, 12), border_radius=2)
    pygame.draw.rect(surf, (102, 156, 150), pygame.Rect(15, 12, 10, 8), border_radius=2)
    pygame.draw.rect(surf, (180, 156, 102), pygame.Rect(28, 12, 6, 8), border_radius=1)
    pygame.draw.rect(surf, (52, 44, 42), pygame.Rect(18, 4, 12, 4), border_radius=2)
    pygame.draw.line(surf, (62, 52, 46), (12, 8), (12, 24), 2)
    pygame.draw.line(surf, (62, 52, 46), (35, 8), (35, 24), 2)
    pygame.draw.line(surf, (46, 40, 38), (8, 16), (40, 16), 1)
    return surf


def _build_sensor() -> pygame.Surface:
    surf = pygame.Surface((24, 48), pygame.SRCALPHA)
    pygame.draw.line(surf, (54, 48, 46), (12, 20), (4, 44), 2)
    pygame.draw.line(surf, (54, 48, 46), (12, 20), (20, 44), 2)
    pygame.draw.line(surf, (54, 48, 46), (12, 20), (12, 44), 2)
    pygame.draw.rect(surf, (88, 92, 98), pygame.Rect(7, 8, 10, 14), border_radius=2)
    pygame.draw.rect(surf, (164, 176, 182), pygame.Rect(8, 9, 8, 12), border_radius=2)
    pygame.draw.line(surf, (66, 58, 52), (12, 0), (12, 8), 2)
    pygame.draw.circle(surf, (106, 206, 198), (12, 12), 2)
    return surf


def _build_monitor() -> pygame.Surface:
    surf = pygame.Surface((36, 28), pygame.SRCALPHA)
    pygame.draw.line(surf, (48, 42, 38), (18, 18), (14, 27), 2)
    pygame.draw.line(surf, (48, 42, 38), (18, 18), (22, 27), 2)
    pygame.draw.rect(surf, (44, 48, 54), pygame.Rect(6, 3, 24, 16), border_radius=2)
    pygame.draw.rect(surf, (80, 130, 126), pygame.Rect(8, 5, 20, 12), border_radius=2)
    pygame.draw.line(surf, (142, 212, 196), (10, 12), (16, 10), 1)
    pygame.draw.line(surf, (142, 212, 196), (16, 10), (22, 13), 1)
    pygame.draw.line(surf, (142, 212, 196), (22, 13), (26, 7), 1)
    return surf


def _draw_label(screen: pygame.Surface, rect: pygame.Rect, text: str, color) -> None:
    label = _font.render(text, True, color)
    outline = _font.render(text, True, (0, 0, 0))
    lx = rect.centerx - label.get_width() // 2
    ly = rect.top - label.get_height() - view.scale(6)
    for ox, oy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        screen.blit(outline, (lx + ox, ly + oy))
    screen.blit(label, (lx, ly))


def _draw_soft_outline(screen: pygame.Surface, rect: pygame.Rect, color) -> None:
    halo = pygame.Surface((rect.width + view.scale(20), rect.height + view.scale(14)), pygame.SRCALPHA)
    pygame.draw.ellipse(halo, (*color, 48), halo.get_rect(), width=max(1, view.scale(2)))
    screen.blit(halo, (rect.centerx - halo.get_width() // 2, rect.centery - halo.get_height() // 2))


def _mix(a, b, t):
    return (
        int(a[0] + (b[0] - a[0]) * t),
        int(a[1] + (b[1] - a[1]) * t),
        int(a[2] + (b[2] - a[2]) * t),
    )
