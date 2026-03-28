"""
core/save.py — Simple JSON save system for The Keeper.

Saves to save.json in the project root.
Stores: current day, elapsed time, active scene, task completion.
"""

import json
import os

_SAVE_PATH = "save.json"

# Scenes that are safe to save/resume from.
# Opening and beach_intro are one-time cutscenes — we never save mid-cutscene.
_SAVEABLE_SCENES = {"lighthouse", "day_night", "nightfall", "beach"}


def save(day: int, elapsed: float, scene: str,
         day_tasks_done: dict, night_tasks_done: dict):
    """Write current game state to save.json."""
    if scene not in _SAVEABLE_SCENES:
        return  # don't save during cutscenes

    data = {
        "day":              day,
        "elapsed":          elapsed,
        "scene":            scene,
        "day_tasks_done":   {str(k): v for k, v in day_tasks_done.items()},
        "night_tasks_done": {str(k): v for k, v in night_tasks_done.items()},
    }
    try:
        with open(_SAVE_PATH, "w") as f:
            json.dump(data, f, indent=2)
    except OSError as e:
        print(f"[save] Could not write save file: {e}")


def load() -> dict | None:
    """
    Load save.json and return its contents as a dict, or None if no save exists.
    Returned dict keys: day, elapsed, scene, day_tasks_done, night_tasks_done.
    """
    if not os.path.exists(_SAVE_PATH):
        return None
    try:
        with open(_SAVE_PATH, "r") as f:
            data = json.load(f)
        # re-key task dicts back to int keys to match tasks.py internals
        data["day_tasks_done"]   = {int(k): v for k, v in data.get("day_tasks_done",   {}).items()}
        data["night_tasks_done"] = {int(k): v for k, v in data.get("night_tasks_done", {}).items()}
        return data
    except (OSError, json.JSONDecodeError, KeyError) as e:
        print(f"[save] Could not read save file: {e}")
        return None


def has_save() -> bool:
    return os.path.exists(_SAVE_PATH)


def delete():
    """Delete the save file (used by New Game)."""
    try:
        if os.path.exists(_SAVE_PATH):
            os.remove(_SAVE_PATH)
    except OSError as e:
        print(f"[save] Could not delete save file: {e}")