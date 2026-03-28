"""
core/sound.py — Central sound manager for The Keeper.

Handles:
  - Environmental ambient layers (birds, crickets, ocean, wind, rain)
  - UI sounds (button click, wire connect, footsteps L/R alternating)
  - Rain system per-day (with narrative logic)
  - Day/night ambient transitions
"""

import pygame
import constants

# ---------------------------------------------------------------------------
# Channel assignments (pygame.mixer has 8 channels by default; we use 6)
# ---------------------------------------------------------------------------
CH_AMBIENT_1   = 0   # birds OR crickets (primary loop)
CH_AMBIENT_2   = 1   # ocean / waves (always present near coast)
CH_AMBIENT_3   = 2   # wind (days 6-10, fades in)
CH_RAIN        = 3   # rain / thunderstorm loop
CH_FOOTSTEP    = 4   # footstep alternation
CH_UI          = 5   # button, wire-connect, etc.

# ---------------------------------------------------------------------------
# Rain narrative schedule
#   Day 4  : Light drizzle — red dust starts falling, eerie quiet broken
#   Day 7  : Heavy rain — fisherman's last goodbye
#   Day 8  : Violent storm — crust fracturing, pitch-black at 3 PM
#   Day 9  : Torrential — sun never rose, world unravelling
#   Day 10 : Full apocalyptic storm — the finale
# ---------------------------------------------------------------------------
RAIN_DAYS = {4, 7, 8, 9, 10}

# Volume scale per day for rain (0.0 = none, 1.0 = full)
RAIN_VOLUME = {
    4:  0.25,   # distant drizzle
    7:  0.60,   # heavy steady rain
    8:  0.80,   # storm
    9:  0.90,   # torrential
    10: 1.00,   # apocalyptic
}


_loaded: dict[str, pygame.mixer.Sound] = {}
_footstep_left  = True          # toggles each step
_footstep_timer = 0.0
_FOOTSTEP_INTERVAL = 0.35       # seconds between steps when moving
_is_night = False
_current_day = 1


def init():
    # Call once after pygame.mixer.init() — loads all sound assets.
    global _loaded, _footstep_left, _footstep_timer, _is_night, _current_day
    pygame.mixer.set_num_channels(8)
    _footstep_left  = True
    _footstep_timer = 0.0
    _is_night       = False
    _current_day    = 1
    _loaded.clear()
    
    env = constants.ENVIRONMENTAL_SOUNDS
    ui  = constants.UI_SOUNDS
    
    paths = {**env, **ui}
    for key, path in paths.items():
        try:
            _loaded[key] = pygame.mixer.Sound(path)
        except (FileNotFoundError, pygame.error):
            pass  # missing asset — silently skip, game still runs
            
    # Pre-set volumes
    _set_vol("waves",         0.25)
    _set_vol("wind",          0.0)   # starts silent
    _set_vol("thunderstorm",  0.0)   # starts silent
    _set_vol("birds",         0.65)
    _set_vol("crickets",      0.40)
    _set_vol("button",        0.35)
    _set_vol("connectWire",   0.5)
    _set_vol("footstepLeft",  0.5)
    _set_vol("footstepRight", 0.5)


def start_day(day: int):
    # Called at the start of each day scene (lighthouse / day_night).
    # Sets up the correct ambient layer for this day.
    global _current_day, _is_night
    _current_day = day
    _is_night    = False
    
    # Stop everything first so we don't layer weirdly
    pygame.mixer.Channel(CH_AMBIENT_1).stop()
    pygame.mixer.Channel(CH_AMBIENT_2).stop()
    pygame.mixer.Channel(CH_AMBIENT_3).stop()
    pygame.mixer.Channel(CH_RAIN).stop()
    
    # Birds during the day
    _play_loop("birds", CH_AMBIENT_1)
    
    # Ocean always present
    _play_loop("waves", CH_AMBIENT_2)
    
    # Wind ramps up from day 6 onwards
    wind_vol = max(0.0, min(0.55, (day - 5) * 0.12))
    _set_vol("wind", wind_vol)
    if wind_vol > 0:
        _play_loop("wind", CH_AMBIENT_3)
    
    # Rain
    if day in RAIN_DAYS:
        _set_vol("thunderstorm", RAIN_VOLUME.get(day, 0.5))
        _play_loop("thunderstorm", CH_RAIN)
    else:
        pygame.mixer.Channel(CH_RAIN).stop()


def start_night(day: int):
    # Called when night begins (nightfall or day_night scene).
    # Swaps birds → crickets, may keep rain going.
    
    global _is_night, _current_day
    _is_night    = True
    _current_day = day
    
    # Swap ambient 1 from birds to crickets
    pygame.mixer.Channel(CH_AMBIENT_1).stop()
    _play_loop("crickets", CH_AMBIENT_1)
    
    # Ocean keeps going
    if not pygame.mixer.Channel(CH_AMBIENT_2).get_busy():
        _play_loop("waves", CH_AMBIENT_2)
    
    # Wind during night (slightly louder)
    wind_vol = max(0.0, min(0.65, (day - 4) * 0.15))
    _set_vol("wind", wind_vol)
    if wind_vol > 0 and not pygame.mixer.Channel(CH_AMBIENT_3).get_busy():
        _play_loop("wind", CH_AMBIENT_3)
    
    # Rain continues / starts on rain nights
    if day in RAIN_DAYS:
        night_rain_vol = min(1.0, RAIN_VOLUME.get(day, 0.5) * 1.2)  # slightly louder at night
        _set_vol("thunderstorm", night_rain_vol)
        if not pygame.mixer.Channel(CH_RAIN).get_busy():
            _play_loop("thunderstorm", CH_RAIN)
    else:
        pygame.mixer.Channel(CH_RAIN).stop()


def stop_all():
    # Stop every channel — call on scene transitions to prevent audio bleed
    for ch in range(8):
        pygame.mixer.Channel(ch).stop()


def play_button():
    _play_once("button", CH_UI)


def play_wire_connect():
    _play_once("connectWire", CH_UI)

def play_vent():
    _play_once("vent", CH_UI)


def update_footsteps(dt: float, is_moving: bool):
    # Call every frame from player.update() (or the scene update).
    # Alternates left/right footstep while the player is walking.
    global _footstep_left, _footstep_timer
    if not is_moving:
        _footstep_timer = 0.0
        return

    _footstep_timer += dt
    if _footstep_timer >= _FOOTSTEP_INTERVAL:
        _footstep_timer = 0.0
        key = "footstepLeft" if _footstep_left else "footstepRight"
        _play_once(key, CH_FOOTSTEP)
        _footstep_left = not _footstep_left


def is_rain_day(day: int) -> bool:
    return day in RAIN_DAYS


def _set_vol(key: str, vol: float):
    if key in _loaded:
        _loaded[key].set_volume(max(0.0, min(1.0, vol)))


def _play_loop(key: str, channel: int):
    if key in _loaded:
        ch = pygame.mixer.Channel(channel)
        ch.play(_loaded[key], loops=-1)


def _play_once(key: str, channel: int):
    if key in _loaded:
        pygame.mixer.Channel(channel).play(_loaded[key])