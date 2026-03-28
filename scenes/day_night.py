"""
Day-Night merged scene (Days 6+).

Sky darkens over time. Emergencies fire with increasing frequency.
Beacon always on unless emergency kills it. HUD shows "Day N?".
Day 10: all emergencies fire at once, screen shakes, then ending sequence.
"""

import math
import pygame
import core.day_cycle as day_cycle
import core.view as view
import entities.player as player
import entities.animations as animations
import scenes.lighthouse as lighthouse
import ui.dialogue as dialogue
import ui.hud as hud
import systems.tasks as tasks
import systems.emergency as emergency
import systems.minigame_overlay as minigame_overlay
import systems.neglect as neglect
import constants

from entities.interactables import Interactable
from entities.visitors import Visitor

done = False

_player = None
_interactables = []
_visitors = []
_font = None
_t = 0.0
_scene_t = 0.0   # time not counting emergency pauses
_beacon_alpha = 1.0
_dim_alpha = 0

_DARKEN_DURATION = 90.0
_SCENE_DURATION = 120.0
_WAIT_AFTER_TASKS = 4.0
_tasks_done_time = None

_emergency_interactables: set = set()   # names currently in emergency mode

# board-door cutscene (Day 7)
_board_door_active   = False
_board_door_timer    = 0.0
_BOARD_DOOR_FADE     = 0.5
_BOARD_DOOR_HOLD     = 1.8
_board_door_alpha    = 0
_board_door_stage    = "idle"
_board_door_task_idx = 0

# screen shake
_shake_t         = 0.0
_shake_intensity = 0.0

# Day 10: all emergencies tracked as a list
_day10_active: list = [] # list of active emergency dicts
_day10_resolved = 0

# ending sequence
_ending_phase = "none"  # "none"|"fade_in"|"text"|"fade_out"|"menu"
_ending_timer = 0.0
_ending_alpha = 0
_ENDING_LINES = [
    "The ground splits.",
    "The water rises.",
    "The lighthouse holds.",
    "The light never goes out.",
]


def init():
    global done, _player, _interactables, _visitors, _font
    global _t, _scene_t, _beacon_alpha, _dim_alpha, _tasks_done_time
    global _shake_t, _shake_intensity, _ending_phase, _ending_timer, _ending_alpha
    global _emergency_interactables, _day10_active, _day10_resolved
    global _board_door_active, _board_door_stage, _board_door_alpha, _board_door_timer
    
    done = False
    _player                  = player.make_player()
    player.reset_world()
    _t                       = 0.0
    _scene_t                 = 0.0
    _beacon_alpha            = 1.0
    _dim_alpha               = 0
    _tasks_done_time         = None
    _shake_t                 = 0.0
    _shake_intensity         = 0.0
    _ending_phase            = "none"
    _ending_timer            = 0.0
    _ending_alpha            = 0
    _emergency_interactables = set()
    _day10_active            = []
    _day10_resolved          = 0
    _board_door_active       = False
    _board_door_stage        = "idle"
    _board_door_alpha        = 0
    _board_door_timer        = 0.0
    _font                    = view.font(11)
    
    dialogue.clear()
    tasks.reset_for_day()
    emergency.reset(day_cycle.day)
    
    day = day_cycle.day
    day_task_list = tasks.get_day_tasks(day)
    
    # queue per interactable, same interactable can have multiple tasks
    interactable_task_queue: dict[str, list[tuple[str, int]]] = {}
    for t in day_task_list:
        if t.get("interactable") and t.get("minigame"):
            name = t["interactable"]
            interactable_task_queue.setdefault(name, []).append((t["minigame"], t["idx"]))
    
    _interactables = []
    for o in constants.INTERACTABLES:
        obj = Interactable(
            o["name"], o["world_x"], o["y"],
            o["w"], o["h"], o["lines"],
            anim_path=o.get("anim_path"), anim_scale=o.get("anim_scale", 1.0))
        if o["name"] in interactable_task_queue:
            queue = list(interactable_task_queue[o["name"]])
            def _make_launcher(q, lines=o["lines"]):
                def _launch():
                    for mg, idx in q:
                        if not tasks.day_task_done(idx):
                            module = minigame_overlay._registry.get(mg)
                            if module and hasattr(module, "set_task_complete_callback"):
                                module.set_task_complete_callback(
                                    lambda i=idx: _notify_task_done(i))
                            minigame_overlay.open(mg)
                            return
                    fallback = lines.get("default", ["Already done."])
                    dialogue.show(fallback, style="thought", default_speaker="player")
                return _launch
            obj.on_use = _make_launcher(queue)
        _interactables.append(obj)
    
    # Mark pending arrows on interactables that have tasks today
    task_names = {t["interactable"] for t in day_task_list if t.get("interactable")}
    for obj in _interactables:
        obj.pending = obj.name in task_names

    door_def = constants.LIGHTHOUSE_DOOR
    door_obj = Interactable(
        "Lighthouse Door", door_def["world_x"], door_def["y"],
        door_def["w"], door_def["h"],
        {"default": ["The lighthouse entrance."]})
    # board_door task: clicking the door triggers the boarding cutscene
    for t in day_task_list:
        if t.get("task_type") == "board_door":
            task_idx = t["idx"]
            def _board_door(idx=task_idx):
                _start_board_door(idx)
            door_obj.on_use = _board_door
            door_obj.pending = True
            break
    _interactables.append(door_obj)
    
    # visitors. fisherman only on his specific days, not via "default"
    _visitors = []
    for v in constants.VISITORS:
        if day in v["lines"] or (v["name"] != "Fisherman" and "default" in v["lines"]):
            _visitors.append(Visitor(
                v["name"], v["world_x"], v["y"],
                v.get("y_offset", 0), v["lines"],
                anim_folder=v.get("anim_folder"), anim_scale=v.get("anim_scale", 1.0)))
    
    intro_lines = list(constants.DAY_NIGHT_TUTORIAL_SCRIPTS.get(day, []))
    script = constants.SCRIPTS.get(day)
    if script:
        intro_lines.extend(script)
    if not intro_lines:
        intro_lines = list(constants.FALLBACK_NIGHT_SCRIPT)
    dialogue.show(intro_lines, style="thought", default_speaker="player")
    
    # Day 10: fire all emergencies immediately
    if day == 10:
        _init_day10_emergencies()


def _start_board_door(task_idx: int):
    global _board_door_active, _board_door_timer, _board_door_alpha
    global _board_door_stage, _board_door_task_idx
    _board_door_active   = True
    _board_door_timer    = 0.0
    _board_door_alpha    = 0
    _board_door_stage    = "fade_in"
    _board_door_task_idx = task_idx


def _init_day10_emergencies():
    global _day10_active
    _day10_active = emergency.fire_all()
    for em in _day10_active:
        _activate_emergency(em, on_complete=lambda e=em: _on_day10_emergency_complete(e))
        # show pending arrow on each emergency interactable
        for obj in _interactables:
            if obj.name == em["interactable"]:
                obj.pending = True
                break
    _trigger_shake(2.0)


def _notify_task_done(idx: int):
    global _tasks_done_time
    tasks.complete_day_task(idx)
    neglect.relieve(constants.NEGLECT_TASK_RELIEF)
    if tasks.all_day_tasks_done() and _tasks_done_time is None:
        _tasks_done_time = _scene_t
        day_finish = constants.DAY_FINISH_SCRIPTS.get(day_cycle.day, [])
        if day_finish:
            dialogue.show(day_finish, style="thought", default_speaker="player")


def _restore_task_on_use(obj):
    day_task_list = tasks.get_day_tasks(day_cycle.day)
    queue = [(t["minigame"], t["idx"])
             for t in day_task_list
             if t.get("interactable") == obj.name and t.get("minigame")]
    if queue:
        def _launch():
            for mg, idx in queue:
                if not tasks.day_task_done(idx):
                    module = minigame_overlay._registry.get(mg)
                    if module and hasattr(module, "set_task_complete_callback"):
                        module.set_task_complete_callback(
                            lambda i=idx: _notify_task_done(i))
                    minigame_overlay.open(mg)
                    return
        obj.on_use = _launch
    else:
        obj.on_use = None
    _emergency_interactables.discard(obj.name)
    obj.pending = False


def _activate_emergency(em: dict, on_complete=None):
    global _emergency_interactables
    for obj in _interactables:
        if obj.name == em["interactable"]:
            _emergency_interactables.add(obj.name)
            mg = em["minigame"]
            cb = on_complete or _on_emergency_complete
            def _launch(mg=mg, callback=cb):
                module = minigame_overlay._registry.get(mg)
                if module:
                    module.reset()
                    if hasattr(module, "set_task_complete_callback"):
                        module.set_task_complete_callback(callback)
                minigame_overlay.open(mg)
            obj.on_use = _launch
            break


def _on_emergency_complete():
    em = emergency.current()
    if em:
        for obj in _interactables:
            if obj.name == em["interactable"]:
                _restore_task_on_use(obj)
                break
    emergency.complete()
    neglect.relieve(constants.NEGLECT_EMERGENCY_RELIEF)
    if day_cycle.day == 10:
        _trigger_shake(1.5)


def _on_day10_emergency_complete(em: dict):
    global _day10_resolved
    _day10_resolved += 1
    neglect.relieve(constants.NEGLECT_EMERGENCY_RELIEF)
    for obj in _interactables:
        if obj.name == em["interactable"]:
            _restore_task_on_use(obj)
            break
    _trigger_shake(1.0)
    if _day10_resolved >= len(_day10_active):
        # all done, start ending
        _start_ending()


def _start_ending():
    global _ending_phase, _ending_timer
    _ending_phase = "fade_in"
    _ending_timer = 0.0


def _trigger_shake(intensity: float):
    global _shake_t, _shake_intensity
    _shake_t = max(_shake_t, 0.8)
    _shake_intensity = max(_shake_intensity, intensity)


def handle_event(event):
    if _ending_phase == "menu":
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if _retry_btn_rect().collidepoint(event.pos):
                import core.game as game
                game.restart()
        return

    if _board_door_active:
        return

    if event.type == pygame.KEYDOWN and event.key in constants.ADVANCE_KEYS:
        dialogue.advance()

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        if not dialogue.active():
            for obj in _interactables + _visitors:
                if obj.handle_click(event.pos, player._world_offset, day_cycle.day):
                    break


def update(dt):
    global _t, _scene_t, _beacon_alpha, _dim_alpha, done
    global _shake_t, _shake_intensity, _ending_phase, _ending_timer, _ending_alpha
    global _board_door_active, _board_door_timer, _board_door_alpha, _board_door_stage

    _t += dt

    # board-door cutscene: freeze everything else while it plays
    if _board_door_active:
        _board_door_timer += dt
        if _board_door_stage == "fade_in":
            _board_door_alpha = min(255, int(255 * (_board_door_timer / _BOARD_DOOR_FADE)))
            if _board_door_timer >= _BOARD_DOOR_FADE:
                _board_door_stage = "hold"
                _board_door_timer = 0.0
        elif _board_door_stage == "hold":
            _board_door_alpha = 255
            if _board_door_timer >= _BOARD_DOOR_HOLD:
                _board_door_stage = "fade_out"
                _board_door_timer = 0.0
        elif _board_door_stage == "fade_out":
            _board_door_alpha = max(0, int(255 * (1.0 - _board_door_timer / _BOARD_DOOR_FADE)))
            if _board_door_timer >= _BOARD_DOOR_FADE:
                _board_door_active = False
                _board_door_stage  = "idle"
                _notify_task_done(_board_door_task_idx)
        return
    
    # update clouds — treat as night once the sky is more than 40% darkened
    _t_dark_now = min(_scene_t / _DARKEN_DURATION, 1.0)
    lighthouse.update_clouds(dt, night=(_t_dark_now > 0.4))
    
    # shake decay
    if _shake_t > 0:
        _shake_t = max(0.0, _shake_t - dt)
        _shake_intensity = max(0.0, _shake_intensity - dt * 1.5)
    
    # ending sequence
    if _ending_phase != "none":
        _ending_timer += dt
        if _ending_phase == "fade_in":
            _ending_alpha = min(255, int(255 * _ending_timer / 2.0))
            if _ending_timer >= 2.0:
                _ending_phase = "text"
                _ending_timer = 0.0
        elif _ending_phase == "text":
            if _ending_timer >= 6.0:
                _ending_phase = "fade_out"
                _ending_timer = 0.0
        elif _ending_phase == "fade_out":
            _ending_alpha = max(0, int(255 * (1.0 - _ending_timer / 1.5)))
            if _ending_timer >= 1.5:
                _ending_phase = "menu"
                _ending_alpha = 0
        return  # freeze world during ending
    
    em_active = len(_emergency_interactables) > 0 or emergency.active()
    
    # scene timer pauses during emergencies
    if not em_active and not dialogue.active():
        _scene_t += dt
    
    # continuous shake on Day 10 while emergencies active
    if day_cycle.day == 10 and em_active and _shake_t <= 0.1:
        _trigger_shake(0.6)
    
    dialogue.update(dt)
    
    if not dialogue.active():
        pending_count, total_pressure_tasks = _pending_pressure_tasks()
        emergency_count = max(len(_emergency_interactables), 1 if emergency.current() else 0)
        pressure = 0.55 + 0.65 * min(_scene_t / _SCENE_DURATION, 1.0)
        rate = 0.0
        if pending_count:
            rate += (
                constants.NEGLECT_DAY_NIGHT_RATE
                * (pending_count / max(total_pressure_tasks, 1))
                * pressure
            )
        if emergency_count:
            rate += constants.NEGLECT_DAY_NIGHT_EMERGENCY_RATE * emergency_count
        if rate > 0.0:
            neglect.add(
                dt * rate,
                "The shift unravels around you. The light cannot hold.",
            )
        else:
            neglect.relieve(dt * constants.NEGLECT_STABILITY_RELIEF)

        player.update(_player, dt)
        mouse_pos = pygame.mouse.get_pos()
        for obj in _interactables + _visitors:
            obj.update(mouse_pos, player._world_offset)
        
        # standard emergency loop
        if day_cycle.day < 10 and not minigame_overlay.is_blocking():
            emergency.update(dt)
            em = emergency.current()
            if em and em["interactable"] not in _emergency_interactables:
                _activate_emergency(em)
    
    # beacon / dim — on Day 10 only consider still-active (unresolved) emergencies
    if day_cycle.day == 10:
        active_day10 = [e for e in _day10_active if e["interactable"] in _emergency_interactables]
        em_source = active_day10
    else:
        em_source = [emergency.current()] if emergency.current() else []
    any_beacon_off = any(e.get("effect") in ("beacon_off", "both") for e in em_source)
    any_dim        = any(e.get("effect") in ("dim", "both")        for e in em_source)
    target_beacon = 0.0 if any_beacon_off else 1.0
    target_dim    = 130 if any_dim else 0
    
    _beacon_alpha = _beacon_alpha + (target_beacon - _beacon_alpha) * min(dt * 3, 1)
    _dim_alpha    = int(_dim_alpha + (target_dim - _dim_alpha) * min(dt * 3, 1))
    
    # scene end (days 6-9 only Day 10 ends via _start_ending)
    if day_cycle.day < 10:
        if _tasks_done_time is not None:
            if _scene_t - _tasks_done_time >= _WAIT_AFTER_TASKS and not dialogue.active():
                done = True
        elif _scene_t >= _SCENE_DURATION:
            done = True


def _shake_offset():
    if _shake_t <= 0 or _shake_intensity <= 0:
        return (0, 0)
    ox = int(math.sin(_t * 80) * _shake_intensity * view.scale(4))
    oy = int(math.cos(_t * 73) * _shake_intensity * view.scale(3))
    return (ox, oy)


def draw(screen):
    ox, oy = _shake_offset()
    
    t_dark = min(_scene_t / _DARKEN_DURATION, 1.0)
    start_col = constants.DAY_SKY_COLORS.get(day_cycle.day, (40, 20, 30))
    r = int(start_col[0] * (1.0 - t_dark * 0.85))
    g = int(start_col[1] * (1.0 - t_dark * 0.85))
    b = int(start_col[2] * (1.0 - t_dark * 0.85))
    screen.fill((r, g, b))
    
    world_surf = pygame.Surface(screen.get_size())
    world_surf.fill((r, g, b))
    
    lighthouse.draw(world_surf, night=(t_dark > 0.4))
    
    pulse = (math.sin(_t * 3.2) + 1.0) * 0.5
    ga = int(18 * _beacon_alpha)
    lighthouse.draw_beacon(
        world_surf, pulse=pulse,
        glow_radius=58, glow_pulse=18,
        glow_alpha=ga, glow_alpha_pulse=int(14 * _beacon_alpha),
        inner_glow_radius=42,
        inner_glow_alpha=int(34 * _beacon_alpha),
        inner_glow_alpha_pulse=int(26 * _beacon_alpha),
        core_radius=int(40 * max(0.05, _beacon_alpha)),
    )
    
    pending = _pending_task_targets()
    emergency_targets = set(_emergency_interactables)
    for obj in _interactables + _visitors:
        is_emergency = obj.name in emergency_targets
        obj.draw(
            world_surf,
            player._world_offset,
            _font,
            highlight=is_emergency or obj.name in pending,
            highlight_color=(210, 82, 82) if is_emergency else (172, 152, 108),
        )
    player.draw(world_surf, _player)
    
    screen.blit(world_surf, (ox, oy))
    
    if _dim_alpha > 0:
        dim = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        dim.fill((0, 0, 0, _dim_alpha))
        screen.blit(dim, (0, 0))
    
    if _board_door_active and _board_door_alpha > 0:
        _draw_board_door_cutscene(screen)
    if _ending_phase != "none":
        _draw_ending(screen)


def _draw_board_door_cutscene(screen):
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, _board_door_alpha))
    screen.blit(overlay, (0, 0))
    if _board_door_alpha > 80:
        font = view.font(16, constants.FONT_PATH)
        lbl  = font.render("You board up the lower doors.", True, (200, 190, 170))
        lbl.set_alpha(_board_door_alpha)
        cr   = view.content_rect()
        screen.blit(lbl, (cr.centerx - lbl.get_width() // 2,
                          cr.centery - lbl.get_height() // 2))


def _draw_ending(screen):
    cr = view.content_rect()
    
    if _ending_phase in ("fade_in", "text", "fade_out"):
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, _ending_alpha))
        screen.blit(overlay, (0, 0))
    
    show_text = _ending_phase == "text" or (_ending_phase == "fade_out" and _ending_timer < 0.5)
    if show_text:
        font_large = view.font(18, constants.FONT_PATH)
        y = cr.centery - view.scale(len(_ENDING_LINES) * 22)
        for line in _ENDING_LINES:
            lbl = font_large.render(line, True, (220, 200, 170))
            screen.blit(lbl, (cr.centerx - lbl.get_width() // 2, y))
            y += lbl.get_height() + view.scale(10)
        
    if _ending_phase == "menu":
        font_large = view.font(18, constants.FONT_PATH)
        font_small = view.font(11, constants.FONT_PATH)
        y = cr.centery - view.scale(len(_ENDING_LINES) * 22)
        for line in _ENDING_LINES:
            lbl = font_large.render(line, True, (220, 200, 170))
            screen.blit(lbl, (cr.centerx - lbl.get_width() // 2, y))
            y += lbl.get_height() + view.scale(10)
        btn = _retry_btn_rect()
        hov = btn.collidepoint(pygame.mouse.get_pos())
        col = (60, 90, 60) if hov else (40, 60, 40)
        pygame.draw.rect(screen, col, btn, border_radius=view.scale(6))
        pygame.draw.rect(screen, (100, 160, 100), btn,
                         width=max(1, view.scale(1)), border_radius=view.scale(6))
        lbl = font_small.render("Try Again", True, (200, 240, 200))
        screen.blit(lbl, (btn.centerx - lbl.get_width() // 2,
                          btn.centery - lbl.get_height() // 2))


def _retry_btn_rect() -> pygame.Rect:
    cr = view.content_rect()
    w, h = view.scale(120), view.scale(36)
    return pygame.Rect(cr.centerx - w // 2, cr.centery + view.scale(80), w, h)


def draw_ui(screen):
    if _ending_phase in ("text", "fade_out", "menu"):
        return
    dialogue.draw(screen, player_rect=view.rect(
        _player["x"], _player["y"], _player["w"], _player["h"]))
    hud.draw_day_night(screen, emergency.current(), _scene_t, _SCENE_DURATION)
    if day_cycle.day == 6 and not dialogue.active() and _scene_t < 18.0:
        hud.draw_help_card(
            screen,
            "Changing Shift",
            [
                "Gold markers are regular chores.",
                "Red markers are urgent failures that interrupt the shift.",
                "The scene timer pauses while emergencies are active.",
                "If either stack up, the Neglect meter keeps climbing.",
            ],
            accent=(196, 110, 88),
        )


def _pending_task_targets() -> set[str]:
    pending = set()
    for task in tasks.get_day_tasks(day_cycle.day):
        idx = task.get("idx", 0)
        if task.get("interactable") and not tasks.day_task_done(idx):
            pending.add(task["interactable"])
        elif task.get("task_type") == "board_door" and not tasks.day_task_done(idx):
            pending.add("Lighthouse Door")
    return pending


def _pending_pressure_tasks() -> tuple[int, int]:
    pending = 0
    total = 0
    for i, task in enumerate(tasks.get_day_tasks(day_cycle.day)):
        if task.get("task_type") == "survive":
            continue
        total += 1
        if not tasks.day_task_done(task.get("idx", i)):
            pending += 1
    return pending, total
