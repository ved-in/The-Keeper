import math
import pygame
import core.day_cycle as day_cycle
import entities.player as player
import scenes.lighthouse as lighthouse
import constants
import ui.dialogue as dialogue
import ui.hud as hud
import core.view as view
import systems.tasks as tasks
import systems.emergency as emergency
import systems.minigame_overlay as minigame_overlay
from entities.interactables import Interactable

# Scene state tracking
done = False
_player = None
_t = 0.0
_phase = "intro"
_interactables = []
_visitors = []
_font = None
_wait_timer = 0.0
_WAIT_DURATION = 5.0
NIGHT_DURATION = 60.0
_night_timer = 0.0
_dim_alpha = 0
_beacon_alpha = 1.0

def init():
    global done, _player, _t, _phase, _font, _interactables, _visitors
    global _wait_timer, _night_timer, _dim_alpha, _beacon_alpha
    
    done = False
    _player = player.make_player()
    _t = 0.0
    _phase = "intro"
    _font = view.font(11)
    _wait_timer = 0.0
    _night_timer = 0.0
    _dim_alpha = 0
    _beacon_alpha = 1.0
    
    tasks.reset_for_night()
    emergency.reset(day_cycle.day)
    
    # Initialize basic interactables
    _interactables = []
    for o in constants.INTERACTABLES:
        obj = Interactable(
            o["name"], o["world_x"], o["y"], o["w"], o["h"], o["lines"],
            anim_path=o.get("anim_path"), anim_scale=o.get("anim_scale", 1.0))
        _interactables.append(obj)
    
    # Initialize visitors with the fixed ground offsets
    from entities.visitors import Visitor
    _visitors = []
    for v in constants.VISITORS:
        if v["name"] == "Fisherman":
            # Hardcoded 25 offset and 2.0 scale to match the intro/day look
            visitor = Visitor(v["name"], v["world_x"], v["y"], 25, v["lines"], anim_key="fisherman", anim_scale=2.0)
        else:
            # Hardcoded 50 offset and 1.8 scale to keep the Scientist grounded
            visitor = Visitor(v["name"], v["world_x"], v["y"], 50, v["lines"], anim_folder=v.get("anim_folder"), anim_scale=1.8)
        _visitors.append(visitor)
        
    dialogue.show(constants.SCRIPTS.get(day_cycle.day, constants.FALLBACK_NIGHT_SCRIPT), style="thought", default_speaker="player")

def _activate_emergency(em: dict) -> None:
    for obj in _interactables:
        if obj.name == em["interactable"]:
            mg = em["minigame"]
            def _launch(mg=mg):
                module = minigame_overlay._registry.get(mg)
                if module and hasattr(module, "set_task_complete_callback"):
                    module.set_task_complete_callback(_on_emergency_complete)
                minigame_overlay.open(mg)
            obj.on_use = _launch
            break

def _deactivate_emergency(em: dict) -> None:
    for obj in _interactables:
        if obj.name == em["interactable"]:
            obj.on_use = None
            break

def _on_emergency_complete() -> None:
    em = emergency.current()
    if em: _deactivate_emergency(em)
    emergency.complete()

def handle_event(event):
    global done, _phase
    if event.type == pygame.KEYDOWN and event.key in constants.ADVANCE_KEYS:
        if _phase == "intro" or _phase == "roaming" or _phase == "outro":
            if not dialogue.advance() and _phase == "intro": _phase = "roaming"

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        if _phase == "roaming" and not dialogue.active():
            for obj in _interactables + _visitors:
                if obj.handle_click(event.pos, player._world_offset, day_cycle.day): break

def update(dt):
    global _t, _wait_timer, _phase, done, _night_timer, _dim_alpha, _beacon_alpha
    _t += dt
    dialogue.update(dt)
    
    if not dialogue.active():
        player.update(_player, dt)
        if _phase == "roaming":
            mouse_pos = pygame.mouse.get_pos()
            for obj in _interactables + _visitors: obj.update(mouse_pos, player._world_offset)
            
            if not minigame_overlay.is_blocking():
                emergency.update(dt)
                em = emergency.current()
                if em and not _get_obj_on_use(em["interactable"]): _activate_emergency(em)
                if not emergency.active():
                    _night_timer += dt
                    if _night_timer >= NIGHT_DURATION: _start_outro()
                        
            em = emergency.current()
            effect = em.get("effect", "dim") if em else None
            target_dim = 130 if effect in ("dim", "both") else 0
            target_beacon = 0.0 if effect in ("beacon_off", "both") else 1.0
            
            _dim_alpha = int(_dim_alpha + (target_dim - _dim_alpha) * min(dt * 3, 1))
            _beacon_alpha = _beacon_alpha + (target_beacon - _beacon_alpha) * min(dt * 3, 1)
            
        elif _phase == "outro":
            _phase = "waiting"
            _wait_timer = 0.0
        elif _phase == "waiting":
            _wait_timer += dt
            if _wait_timer >= _WAIT_DURATION: done = True

def _get_obj_on_use(interactable_name: str):
    for obj in _interactables:
        if obj.name == interactable_name: return obj.on_use
    return None

def _start_outro():
    global _phase
    _phase = "outro"
    dialogue.show(constants.FINISH_SCRIPTS.get(day_cycle.day, ["The night passes."]), style="thought", default_speaker="player")

def draw(screen):
    screen.fill(constants.SKY_COLORS["night"])
    lighthouse.draw(screen)

    # Beacon pulse calculation
    pulse = (math.sin(_t * 3.2) + 1.0) * 0.5
    ga = int(18 * _beacon_alpha)
    ia = int(34 * _beacon_alpha)
    
    lighthouse.draw_beacon(
        screen, pulse=pulse, glow_radius=58, glow_pulse=18, glow_alpha=ga, 
        glow_alpha_pulse=int(14 * _beacon_alpha), inner_glow_radius=42, 
        inner_glow_alpha=ia, inner_glow_alpha_pulse=int(26 * _beacon_alpha),
        core_radius=int(40 * max(0.05, _beacon_alpha))
    )
    
    for obj in _interactables + _visitors:
        if obj.name == "Fisherman": obj.draw(screen, player._world_offset, _font, flip=True)
        else: obj.draw(screen, player._world_offset, _font)
        
    player.draw(screen, _player)
    
    if _dim_alpha > 0:
        dim = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        dim.fill((0, 0, 0, _dim_alpha))
        screen.blit(dim, (0, 0))

def draw_ui(screen):
    hud.draw_night(screen, _night_timer, NIGHT_DURATION, emergency.current())
    dialogue.draw(screen, player_rect=view.rect(_player["x"], _player["y"], _player["w"], _player["h"]))