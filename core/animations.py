import os
import pygame

# { 
#  entity_name: {
#               state: [frames] 
#               }
# }

_animations = {}

# { entity_name: { "frame": int, "timer": float } }
_state = {}

ANIM_SPEED = 0.12


def load_folder(path, scale=1.0):
    frames = []
    i = 1
    while True:
        filepath = os.path.join(path, f"frame{i}.png")
        if not os.path.exists(filepath):
            break
        frame = pygame.image.load(filepath).convert_alpha()
        if scale != 1.0:
            w, h = frame.get_size()
            frame = pygame.transform.scale(frame, (int(w * scale), int(h * scale)))
        frames.append(frame)
        i += 1
    return frames


def register(entity, state, path, scale=1.0):
    if entity not in _animations:
        _animations[entity] = {}
        _state[entity] = {"frame": 0, "timer": 0.0}
    _animations[entity][state] = load_folder(path, scale)


def load_all():
    register("mc", "idle", "assets/characters/mc/idle", scale=1.1)
    register("mc", "walk", "assets/characters/mc/walk", scale=1.1)


def update(dt):
    """Call once per tick — advances all entity frames."""
    for entity, s in _state.items():
        s["timer"] += dt
        if s["timer"] >= ANIM_SPEED:
            s["timer"] = 0.0
            # frame count depends on current state — we don't track state here
            # so just increment and let get_frame wrap it
            s["frame"] += 1


def get_frame(entity, anim_state, flip=False):
    frames = _animations.get(entity, {}).get(anim_state, [])
    if not frames:
        return None
    frame = frames[_state[entity]["frame"] % len(frames)]
    if flip:
        frame = pygame.transform.flip(frame, True, False)
    return frame
    
def reset(entity):
    if entity in _state:
        _state[entity]["frame"] = 0
        _state[entity]["timer"] = 0.0