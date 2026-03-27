import os
import pygame

# stores all loaded animation frames grouped by entity name and state name
# structure: { entity_name: { state_name: [pygame.Surface, ...] } }
_animations = {}

# stores the current frame index and timer for each entity
# structure: { entity_name: { "frame": int, "timer": float } }
_state = {}

# seconds between each frame switch
ANIM_SPEED = 0.12


def load_folder(path, scale=1.0):
    # loads frames named frame1.png, frame2.png, ... until it runs out of files
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
    # sets up storage for a new entity if this is the first state being registered
    if entity not in _animations:
        _animations[entity] = {}
        _state[entity] = {"frame": 0, "timer": 0.0}
    _animations[entity][state] = load_folder(path, scale)


def load_all():
    # register all entities and their animation states here
    # fisherman has separate folders for each animation state with individual frame files
    register("fisherman", "idle", "assets/characters/fisherman/idle", scale=1.0)
    register("fisherman", "walk", "assets/characters/fisherman/walk", scale=1.0)
    register("fisherman", "hook", "assets/characters/fisherman/hook", scale=1.0)
    register("fisherman", "fish", "assets/characters/fisherman/fish", scale=1.0)
    
    register("mc", "idle", "assets/characters/mc/idle", scale=1.1)
    register("mc", "walk", "assets/characters/mc/walk", scale=1.1)


def update(dt):
    # called once per game tick to advance every entity's frame counter
    for entity, s in _state.items():
        s["timer"] += dt
        if s["timer"] >= ANIM_SPEED:
            s["timer"] = 0.0
            # increment unconditionally, get_frame handles the modulo wrap
            s["frame"] += 1


def get_frame(entity, anim_state, flip=False):
    frames = _animations.get(entity, {}).get(anim_state, [])
    if not frames:
        return None
    # wrap the frame index so it loops back to the start after the last frame
    frame = frames[_state[entity]["frame"] % len(frames)]
    if flip:
        frame = pygame.transform.flip(frame, True, False)
    return frame
    
def reset(entity):
    # resets the frame counter to zero when switching animation states
    # so the new animation always starts from its first frame
    if entity in _state:
        _state[entity]["frame"] = 0
        _state[entity]["timer"] = 0.0
