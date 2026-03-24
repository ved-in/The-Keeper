import math
import pygame
import core.day_cycle as day_cycle
import core.player as player
import scenes.lighthouse as lighthouse
import constants
import ui.dialogue as dialogue
import ui.hud as hud
import core.view as view
import core.tasks as tasks
from core.interactables import Interactable


import core.minigame_overlay as minigame_overlay
import minigames.clean_lens as clean_lens

# set to True when the player finishes reading, signals game.py to advance the day
done = False
_player = player.make_player()
# tracks total time spent in this scene, used to drive the beacon pulse animation
_t = 0.0

# "intro"    -> player reads the night dialogue
# "roaming"  -> dialogue done, player can click the task interactable to start the minigame
# "task"     -> minigame running
# "outro"    -> post-minigame dialogue
# "waiting"  -> outro done, 5-second pause before switching to day
_phase = "intro"

_interactables = []
_font = None
_wait_timer = 0.0  # counts down after outro dialogue finishes before switching to day
_WAIT_DURATION = 5.0


def init():
    global done, _player, _t, _phase, _font, _interactables, _wait_timer
    done = False
    _player = player.make_player()
    _t = 0.0
    _phase = "intro"
    _font = view.font(11)
    _wait_timer = 0.0
    tasks.reset_for_night()

    night_task = constants.NIGHT_TASKS.get(day_cycle.day, {})
    task_name = night_task.get("interactable")
    task_minigame = night_task.get("minigame")

    _interactables = []
    for o in constants.INTERACTABLES:
        obj = Interactable(
            o["name"],
            o["world_x"], o["y"],
            o["w"], o["h"], o["lines"],
            anim_path=o.get("anim_path"), anim_scale=o.get("anim_scale", 1.0))
        if task_minigame and task_name == o["name"]:
            def _launch(mg=task_minigame):
                clean_lens.set_task_complete_callback(notify_task_done)
                minigame_overlay.open(mg)
            obj.on_use = _launch
        _interactables.append(obj)
    
    # load the correct night script as soon as the scene starts
    dialogue.show(constants.SCRIPTS.get(day_cycle.day, constants.FALLBACK_NIGHT_SCRIPT), style="thought", default_speaker="player")


def _start_outro():
    global _phase
    _phase = "outro"
    dialogue.show(constants.FINISH_SCRIPTS.get(day_cycle.day, ["The night passes."]), style="thought", default_speaker="player")


def notify_task_done():
    tasks.complete_night_task()
    _start_outro()


def handle_event(event):
    global done, _phase
    if event.type == pygame.KEYDOWN and event.key in constants.ADVANCE_KEYS:
        if _phase == "intro":
            if not dialogue.advance():
                if not tasks.get_night_minigame(day_cycle.day):
                    _start_outro()
                else:
                    _phase = "roaming"
        elif _phase == "roaming":
            dialogue.advance()
        elif _phase == "outro":
            dialogue.advance()

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        if _phase == "roaming" and not dialogue.active():
            for obj in _interactables:
                if obj.handle_click(event.pos, player._world_offset, day_cycle.day):
                    break


def update(dt):
    global _t, _wait_timer, _phase, done
    _t += dt
    dialogue.update(dt)
    # block player movement while the dialogue is showing
    if not dialogue.active():
        player.update(_player, dt)
        if _phase == "roaming":
            mouse_pos = pygame.mouse.get_pos()
            for obj in _interactables:
                obj.update(mouse_pos, player._world_offset)
        elif _phase == "outro":
            # outro dialogue just finished — start the 5-second wait
            _phase = "waiting"
            _wait_timer = 0.0
        elif _phase == "waiting":
            _wait_timer += dt
            if _wait_timer >= _WAIT_DURATION:
                done = True


def draw(screen):
    screen.fill(constants.SKY_COLORS["night"])
    lighthouse.draw(screen)

    # sin wave gives a smooth 0 to 1 to 0 pulse value
    pulse = (math.sin(_t * 3.2) + 1.0) * 0.5
    lighthouse.draw_beacon(
        screen,
        pulse=pulse,
        glow_radius=58,
        glow_pulse=18,
        glow_alpha=18,
        glow_alpha_pulse=14,
        inner_glow_radius=42,
        inner_glow_alpha=34,
        inner_glow_alpha_pulse=26,
        core_radius=40,
    )
    for obj in _interactables:
        obj.draw(screen, player._world_offset, _font)
    player.draw(screen, _player)

def draw_ui(screen):
    hud.draw_night(screen)
    dialogue.draw(screen, player_rect=view.rect(_player["x"], _player["y"], _player["w"], _player["h"]))