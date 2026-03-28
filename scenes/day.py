import pygame
import entities.player as player
import ui.dialogue as dialogue
import ui.hud as hud
import scenes.lighthouse as lighthouse
import constants
import core.view as view
import core.day_cycle as day_cycle
import systems.tasks as tasks
import systems.minigame_overlay as minigame_overlay

from entities.interactables import Interactable
from entities.visitors import Visitor

# "roaming" -> player explores, can click the task interactable to start minigame
# "task"    -> minigame running
# "outro"   -> post-task dialogue (only shown if a task was completed)
_phase = "roaming"

_interactables = []
_visitors = []
_font = None

_board_door_active   = False
_board_door_timer    = 0.0
_BOARD_DOOR_FADE     = 0.5
_BOARD_DOOR_HOLD     = 1.8
_board_door_alpha    = 0
_board_door_stage    = "idle"
_board_door_task_idx = 0


def init():
    global _player, _interactables, _visitors, _font, _phase
    global _board_door_active, _board_door_stage
    _player = player.make_player()
    # reset the world scroll so every new day starts from the same position
    player.reset_world()
    dialogue.clear()
    _phase             = "roaming"
    _font              = view.font(11)
    _board_door_active = False
    _board_door_stage  = "idle"
    tasks.reset_for_day()

    day           = day_cycle.day
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
                                    lambda i=idx: notify_task_done(i))
                            minigame_overlay.open(mg)
                            return
                    fallback = lines.get("default", ["Already done."])
                    dialogue.show(fallback, style="thought", default_speaker="player")
                return _launch
            obj.on_use = _make_launcher(queue)
        _interactables.append(obj)

    # lighthouse door is always present, board_door task on day 7 makes it interactive
    door_def = constants.LIGHTHOUSE_DOOR
    door_obj = Interactable(
        "Lighthouse Door", door_def["world_x"], door_def["y"],
        door_def["w"], door_def["h"],
        {"default": ["The lighthouse entrance."]})
    for t in day_task_list:
        if t.get("task_type") == "board_door":
            task_idx = t["idx"]
            def _board_door(idx=task_idx):
                _start_board_door(idx)
            door_obj.on_use = _board_door
            break
    _interactables.append(door_obj)
    
    _visitors = []
    for v in constants.VISITORS:
        visitor = Visitor(
            v["name"], v["world_x"], v["y"],
            v.get("y_offset", 0), v["lines"],
            anim_folder=v.get("anim_folder"),
            anim_scale=v.get("anim_scale", 1.0)
        )
        _visitors.append(visitor)

    start_lines = constants.DAY_START_SCRIPTS.get(day)
    if start_lines:
        dialogue.show(start_lines, style="thought", default_speaker="player")
    _refresh_pending_flags()


def _start_board_door(task_idx: int):
    global _board_door_active, _board_door_timer, _board_door_alpha
    global _board_door_stage, _board_door_task_idx
    _board_door_active   = True
    _board_door_timer    = 0.0
    _board_door_alpha    = 0
    _board_door_stage    = "fade_in"
    _board_door_task_idx = task_idx


def notify_task_done(idx: int = 0):
    """Called by a day minigame when it completes."""
    global _phase
    tasks.complete_day_task(idx)
    _refresh_pending_flags()
    if tasks.all_day_tasks_done():
        _phase = "outro"
        day_finish = constants.DAY_FINISH_SCRIPTS.get(day_cycle.day, [])
        if day_finish:
            dialogue.show(day_finish, style="thought", default_speaker="player")


def _active_visitors():
    return [v for v in _visitors if day_cycle.day in v.lines_by_day or "default" in v.lines_by_day]


def handle_event(event):
    global _phase
    if _board_door_active:
        return
    
    if event.type == pygame.KEYDOWN and event.key in constants.ADVANCE_KEYS:
        dialogue.advance()

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        if not dialogue.active():
            if day_cycle.day in constants.BEACH_DAYS:
                if _beach_btn_rect().collidepoint(event.pos):
                    import core.game as game
                    game.switch("beach")
                    return
            if tasks.all_day_tasks_done():
                if hud.skip_btn_rect().collidepoint(event.pos):
                    import core.game as game
                    game.skip_to_night()
                    return
            for obj in _interactables + _visitors:
                if obj.handle_click(event.pos, player._world_offset, day_cycle.day):
                    break


def update(dt):
    global _board_door_active, _board_door_timer, _board_door_alpha, _board_door_stage
    
    lighthouse.update_clouds(dt, night=False)
    
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
                notify_task_done(_board_door_task_idx)
        return
    
    dialogue.update(dt)
    if not dialogue.active():
        player.update(_player, dt)
        mouse_pos = pygame.mouse.get_pos()
        for obj in _interactables + _visitors:
            obj.update(mouse_pos, player._world_offset)


def draw(screen):
    lighthouse.draw(screen, night=False)
    pending = _pending_task_targets()
    for obj in _interactables + _visitors:
        obj.draw(
            screen,
            player._world_offset,
            _font,
            highlight=(obj.name in pending),
        )
    player.draw(screen, _player)
    if _board_door_active and _board_door_alpha > 0:
        _draw_board_door_cutscene(screen)


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


def draw_ui(screen):
    dialogue.draw(screen, player_rect=view.rect(_player["x"], _player["y"], _player["w"], _player["h"]))
    hud.draw(screen)
    if tasks.all_day_tasks_done():
        hud.draw_skip_button(screen)
    if day_cycle.day in constants.BEACH_DAYS:
        _draw_beach_button(screen)
    help_card = _help_card()
    if help_card and not dialogue.active():
        title, lines, accent = help_card
        hud.draw_help_card(screen, title, lines, accent=accent)


def _beach_btn_rect() -> pygame.Rect:
    return view.rect(10, 490, 72, 22)


def _draw_beach_button(screen):
    r = _beach_btn_rect()
    font = view.font(9, constants.FONT_PATH)
    hov = r.collidepoint(pygame.mouse.get_pos())
    col = (60, 90, 130) if hov else (40, 60, 90)
    pygame.draw.rect(screen, col, r, border_radius=view.scale(4))
    pygame.draw.rect(screen, (80, 110, 160), r,
                     width=max(1, view.scale(1)), border_radius=view.scale(4))
    lbl = font.render("→ Beach", True, (180, 210, 240))
    screen.blit(lbl, (r.centerx - lbl.get_width() // 2,
                      r.centery - lbl.get_height() // 2))


def _pending_task_targets() -> set[str]:
    pending = set()
    for task in tasks.get_day_tasks(day_cycle.day):
        idx = task.get("idx", 0)
        if task.get("interactable") and not tasks.day_task_done(idx):
            pending.add(task["interactable"])
        elif task.get("task_type") == "board_door" and not tasks.day_task_done(idx):
            pending.add("Lighthouse Door")
    return pending


def _help_card():
    if tasks.all_day_tasks_done():
        return (
            "Next Step",
            [
                "Day chores are finished.",
                "Use Skip to Night at the bottom-left when you are ready.",
            ],
            (92, 168, 108),
        )

    if day_cycle.day == 1:
        pending = _pending_task_targets()
        if pending == {"Lens"}:
            return (
                "Next Task",
                [
                    "The lens is the light at the top of the tower.",
                    "Stand near the lighthouse and click the highlighted lens.",
                ],
                (172, 152, 108),
            )
        return (
            "Tutorial",
            [
                "Gold markers show your current chores.",
                "Click nearby highlighted objects to start their repair task.",
                "The lighthouse door is not an interior transition.",
            ],
            (172, 152, 108),
        )

    if day_cycle.day in constants.BEACH_DAYS:
        for task in tasks.get_day_tasks(day_cycle.day):
            if task.get("task_type") == "beach" and not tasks.day_task_done(task.get("idx", 0)):
                return (
                    "Beach Task",
                    [
                        "The scientist's errand happens at the beach.",
                        "Use the Beach button once you want to handle that job.",
                    ],
                    (120, 164, 214),
                )

    return None


def _refresh_pending_flags():
    pending_names = _pending_task_targets()
    for obj in _interactables:
        obj.pending = obj.name in pending_names
    for visitor in _visitors:
        visitor.pending = day_cycle.day in visitor.lines_by_day
