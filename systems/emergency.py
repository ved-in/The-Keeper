import random

EMERGENCY_POOL = [
    {"name": "Generator Failure",  "interactable": "Generator",    "minigame": "minigame_wires",    "effect": "beacon_off"},
    #{"name": "Breaker Tripped",    "interactable": "Breaker Box",  "minigame": "minigame_breakers", "effect": "beacon_off"},
    {"name": "Lens Fouled",        "interactable": "Lens",         "minigame": "minigame_clean",    "effect": "dim"},
    #{"name": "Engine Overheating", "interactable": "Engine",       "minigame": "minigame_valves",   "effect": "dim"},
    #{"name": "Motor Stalling",     "interactable": "Light Motor",  "minigame": "minigame_crank",    "effect": "beacon_off"},
]

_MIN_DELAY = 8.0
_MAX_DELAY = 18.0

_EMERGENCIES_PER_NIGHT = {
    1: 1,
    2: 1,
    3: 1,
    4: 2,
    5: 2,
    6: 2,
    7: 3,
    8: 3,
    9: 3,
    10: 4,
}

_active_emergency = None
_next_trigger     = 0.0
_resolved_count   = 0
_required_count   = 1
_elapsed          = 0.0
_all_done_flag    = False


def reset(day: int) -> None:
    global _active_emergency, _next_trigger, _resolved_count
    global _required_count, _elapsed, _all_done_flag
    
    _active_emergency = None
    _resolved_count = 0
    _required_count = _EMERGENCIES_PER_NIGHT.get(day, 1)
    _elapsed = 0.0
    _all_done_flag = False
    _schedule_next()


def update(dt: float) -> None:
    global _elapsed, _active_emergency
    if _all_done_flag:
        return
    if _active_emergency is not None:
        return
    
    _elapsed += dt
    if _elapsed >= _next_trigger:
        _fire_next()


def active() -> bool:
    return _active_emergency is not None


def current() -> dict | None:
    return _active_emergency


def complete() -> None:
    global _active_emergency, _resolved_count, _all_done_flag
    _active_emergency = None
    _resolved_count  += 1
    if _resolved_count >= _required_count:
        _all_done_flag = True
    else:
        _schedule_next()


def all_done() -> bool:
    return _all_done_flag


def _schedule_next() -> None:
    global _next_trigger, _elapsed
    _elapsed = 0.0
    _next_trigger = random.uniform(_MIN_DELAY, _MAX_DELAY)


def _fire_next() -> None:
    global _active_emergency
    _active_emergency = random.choice(EMERGENCY_POOL)