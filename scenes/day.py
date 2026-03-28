import pygame
import entities.player as player
import ui.dialogue as dialogue
import ui.hud as hud
import scenes.lighthouse as lighthouse
import constants
import core.view as view
import core.day_cycle as day_cycle
import systems.tasks as tasks
from entities.interactables import Interactable
from entities.visitors import Visitor

_phase = "roaming"
_interactables = []
_visitors = []
_font = None
_player = None

def init():
    global _player, _interactables, _visitors, _font, _phase
    _player = player.make_player()
    player.reset_world()
    dialogue.clear()
    _phase = "roaming"
    _font = view.font(11)
    tasks.reset_for_day()

    day_task_list = tasks.get_day_tasks(day_cycle.day)
    task_map = {t["interactable"]: (t["minigame"], i) for i, t in enumerate(day_task_list) if t.get("interactable") and t.get("minigame")}

    _interactables = []
    for o in constants.INTERACTABLES:
        obj = Interactable(o["name"], o["world_x"], o["y"], o["w"], o["h"], o["lines"], anim_path=o.get("anim_path"), anim_scale=o.get("anim_scale", 1.0))
        if o["name"] in task_map:
            mg, task_idx = task_map[o["name"]]
            def _launch(mg=mg, idx=task_idx):
                import systems.minigame_overlay as minigame_overlay
                module = minigame_overlay._registry.get(mg)
                if module and hasattr(module, "set_task_complete_callback"):
                    module.set_task_complete_callback(lambda i=idx: notify_task_done(i))
                minigame_overlay.open(mg)
            obj.on_use = _launch
        _interactables.append(obj)

    _visitors = []
    for v in constants.VISITORS:
        # Fisherman:
        if v["name"] == "Fisherman":
            visitor = Visitor(v["name"], v["world_x"], v["y"], v.get("y_offset", 25), v["lines"], anim_key="fisherman", anim_scale=2.0)
        # Scientist/Others:
        else:
            # hardcoded 50 to FORCE the Scientist to move down
            # Dont use v.get() if you want to override the value manually. using v.get() made it ignore the offset i passed
            visitor = Visitor(v["name"], v["world_x"], v["y"], 50, v["lines"], anim_folder=v.get("anim_folder"), anim_scale=1.8)
        _visitors.append(visitor)

def notify_task_done(idx: int = 0):
    global _phase
    tasks.complete_day_task(idx)
    if tasks.all_day_tasks_done():
        _phase = "outro"
        day_finish = constants.DAY_FINISH_SCRIPTS.get(day_cycle.day, [])
        if day_finish: dialogue.show(day_finish, style="thought", default_speaker="player")

def _active_visitors():
    return [v for v in _visitors if day_cycle.day in v.lines_by_day or "default" in v.lines_by_day]

def handle_event(event):
    global _phase
    if event.type == pygame.KEYDOWN and event.key in constants.ADVANCE_KEYS:
        dialogue.advance()
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        if not dialogue.active():
            for obj in _interactables + _active_visitors():
                if obj.handle_click(event.pos, player._world_offset, day_cycle.day): break

def update(dt):
    dialogue.update(dt)
    if not dialogue.active():
        player.update(_player, dt)
        mouse_pos = pygame.mouse.get_pos()
        for obj in _interactables + _active_visitors():
            obj.update(mouse_pos, player._world_offset)

def draw(screen):
    lighthouse.draw(screen)
    for obj in _interactables + _active_visitors():
        if obj.name == "Fisherman":
            obj.draw(screen, player._world_offset, _font, flip=True)
        else:
            obj.draw(screen, player._world_offset, _font)
    player.draw(screen, _player)

def draw_ui(screen):
    dialogue.draw(screen, player_rect=view.rect(_player["x"], _player["y"], _player["w"], _player["h"]))
    hud.draw(screen)