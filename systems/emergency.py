import random

EMERGENCY_POOL = [
    {"name": "Generator Failure",  "interactable": "Generator",   "minigame": "minigame_wires",    "effect": "beacon_off"},
    {"name": "Breaker Tripped",    "interactable": "Breaker Box", "minigame": "minigame_breakers", "effect": "beacon_off"},
    {"name": "Lens Fouled",        "interactable": "Lens",        "minigame": "minigame_clean",    "effect": "dim"},
    {"name": "Engine Overheating", "interactable": "Engine",      "minigame": "minigame_valves",   "effect": "dim"},
]

# delays shrink as days progress
# emergencies get more frequent
_MIN_DELAY_BY_DAY = {6: 18, 7: 14, 8: 10, 9: 7,  10: 0}
_MAX_DELAY_BY_DAY = {6: 30, 7: 22, 8: 16, 9: 12, 10: 0}

# night number: number of emergency
_EMERGENCIES_PER_SCENE = {
    1: 1, 2: 1, 3: 1, 4: 2, 5: 2,
    6: 2, 7: 3, 8: 3, 9: 4, 10: 69420,  # Day 10: fire all, tracked differently
}

_active_emergency  = None
_next_trigger      = 0.0
_resolved_count    = 0
_required_count    = 1
_elapsed           = 0.0
_all_done_flag     = False
_current_day       = 1
_last_emergency    = None   # prevent same emergency back-to-back


def reset(day: int) -> None:
    global _active_emergency, _next_trigger, _resolved_count
    global _required_count, _elapsed, _all_done_flag, _current_day, _last_emergency
    
    _active_emergency = None
    _resolved_count   = 0
    _required_count   = _EMERGENCIES_PER_SCENE.get(day, 1)
    _elapsed          = 0.0
    _all_done_flag    = False
    _current_day      = day
    _last_emergency   = None
    _schedule_next()


def update(dt: float) -> None:
    global _elapsed
    if _all_done_flag or _active_emergency is not None:
        return
    
    _elapsed += dt
    if _elapsed >= _next_trigger:
        _fire_next()


def active() -> bool:
    return _active_emergency is not None


def current() -> dict | None:
    return _active_emergency


def complete() -> None:
    global _active_emergency, _resolved_count, _all_done_flag, _last_emergency
    _last_emergency   = _active_emergency
    _active_emergency = None
    _resolved_count  += 1
    if _current_day != 10 and _resolved_count >= _required_count:
        _all_done_flag = True
    else:
        _schedule_next()


def all_done() -> bool:
    return _all_done_flag


def _schedule_next() -> None:
    global _next_trigger, _elapsed
    _elapsed = 0.0
    min_d = _MIN_DELAY_BY_DAY.get(_current_day, 8)
    max_d = _MAX_DELAY_BY_DAY.get(_current_day, 18)
    _next_trigger = random.uniform(min_d, max_d)


def _fire_next() -> None:
    global _active_emergency
    if _current_day == 10:
        return  # Day 10 uses fire_all externally
    pool = [e for e in EMERGENCY_POOL if e is not _last_emergency] # Prevents same emergency repeating
    if not pool:
        pool = EMERGENCY_POOL
    _active_emergency = random.choice(pool)


def fire_all() -> list[dict]:
    """Day 10: return all emergencies at once (caller handles them as a list)."""
    return list(EMERGENCY_POOL)


def pending_count() -> int:
    """How many more emergencies are queued."""
    return max(0, _required_count - _resolved_count)