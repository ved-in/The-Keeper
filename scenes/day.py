import pygame
import core.player as player
import ui.dialogue as dialogue
import ui.hud as hud
import scenes.lighthouse as lighthouse
import constants
import core.view as view
import core.day_cycle as day_cycle
import core.tasks as tasks

from core.interactables import Interactable
from core.visitors import Visitor

# "roaming" -> player explores, can click the task interactable to start minigame
# "task"    -> minigame running
# "outro"   -> post-task dialogue (only shown if a task was completed)
_phase = "roaming"

_interactables = []
_visitors = []
_font = None


def init():
    global _player, _interactables, _visitors, _font, _phase
    _player = player.make_player()
    # reset the world scroll so every new day starts from the same position
    player.reset_world()
    dialogue.clear()
    _phase = "roaming"
    _font = view.font(11)
    tasks.reset_for_day()

    day_task = constants.DAY_TASKS.get(day_cycle.day, {})
    task_name = day_task.get("interactable")
    task_minigame = day_task.get("minigame")

    _interactables = []
    for o in constants.INTERACTABLES:
        obj = Interactable(
            o["name"],
            o["world_x"], o["y"],
            o["w"], o["h"], o["lines"],
            anim_path=o.get("anim_path"), anim_scale=o.get("anim_scale", 1.0))
        if task_minigame and task_name == o["name"]:
            def _launch(mg=task_minigame):
                import core.minigame_overlay as minigame_overlay
                import minigames.clean_lens as clean_lens
                clean_lens.set_task_complete_callback(notify_task_done)
                minigame_overlay.open(mg)
            obj.on_use = _launch
        _interactables.append(obj)

    _visitors = [
        Visitor(
            v["name"],
            v["world_x"], v["y"],
            v.get("y_offset", 0),
            v["lines"],
            anim_folder=v.get("anim_folder"), anim_scale=v.get("anim_scale", 1.0)
        )
        for v in constants.VISITORS
    ]


def notify_task_done():
    """Called by a day minigame when it completes."""
    global _phase
    tasks.complete_day_task()
    _phase = "outro"
    day_finish = constants.DAY_FINISH_SCRIPTS.get(day_cycle.day, [])
    if day_finish:
        dialogue.show(day_finish, style="thought", default_speaker="player")


def _active_visitors():
    return [v for v in _visitors if day_cycle.day in v.lines_by_day or "default" in v.lines_by_day]


def handle_event(event):
    global _phase
    if event.type == pygame.KEYDOWN and event.key in constants.ADVANCE_KEYS:
        dialogue.advance()

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        if not dialogue.active():
            for obj in _interactables + _active_visitors():
                if obj.handle_click(event.pos, player._world_offset, day_cycle.day):
                    break


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
        obj.draw(screen, player._world_offset, _font)
    player.draw(screen, _player)


def draw_ui(screen):
    dialogue.draw(screen, player_rect=view.rect(_player["x"], _player["y"], _player["w"], _player["h"]))
    hud.draw(screen)
