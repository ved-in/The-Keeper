import core.day_cycle as day_cycle
import scenes.lighthouse as lighthouse
import scenes.day as day
import scenes.day_night as day_night
import scenes.nightfall as nightfall
import scenes.start_screen as start_screen
import scenes.opening as opening
import scenes.beach_intro as beach_intro
import scenes.beach as beach
import entities.animations as animations
import systems.tasks as tasks
import systems.minigame_overlay as minigame_overlay
import constants

import pygame

# maps scene name strings to their modules so we can switch between them easily
SCENES = {
    "start_screen": start_screen,
    "opening":     opening,
    "beach_intro": beach_intro,
    "lighthouse":  day,
    "day_night":   day_night,
    "nightfall":   nightfall,
    "beach":       beach,
}

RESET_ON_ENTER = {"start_screen", "opening", "beach_intro", "nightfall", "lighthouse", "day_night", "beach"}

# Scenes that are just side-trips from the day scene, returning to lighthouse
# from these should NOT re-init the day (which would reset task progress).
_BEACH_SIDE_TRIPS = {"beach"}

scene = "opening"

_fade_alpha = 0
_fading_in = False
_fading_out = False
_pending_scene = None
FADE_SPEED = 200


def init():
    day_cycle.init()
    lighthouse.init()
    day.init()
    # load all sprite sheets before the game loop starts
    animations.load_all()
    
    import minigames.clean_lens        as clean_lens
    import minigames.fix_wires         as fix_wires
    import minigames.flip_breakers     as flip_breakers
    import minigames.pressure_valves   as pressure_valves
    import minigames.manual_crank      as manual_crank
    import minigames.log_pressure      as log_pressure
    import minigames.lubricate_engine  as lubricate_engine
    import minigames.refuel_generator  as refuel_generator

    minigame_overlay.register("minigame_clean",    clean_lens.instance)
    minigame_overlay.register("minigame_wires",    fix_wires.instance)
    minigame_overlay.register("minigame_breakers", flip_breakers.instance)
    minigame_overlay.register("minigame_valves",   pressure_valves.instance)
    minigame_overlay.register("minigame_crank",    manual_crank.instance)
    minigame_overlay.register("minigame_pressure", log_pressure.instance)
    minigame_overlay.register("minigame_lube",     lubricate_engine.instance)
    minigame_overlay.register("minigame_refuel",   refuel_generator.instance)
    minigame_overlay.reset_all()
    # start on the title/start screen
    global scene
    scene = "start_screen"
    start_screen.init()


def switch(name):
    global _pending_scene, _fading_in
    _pending_scene = name
    _fading_in = True  # start fading to black


def skip_to_night():
    global _pending_scene, _fading_in
    _pending_scene = "nightfall"
    _fading_in = True


def restart():
    global scene, _fade_alpha, _fading_in, _fading_out, _pending_scene
    _fade_alpha    = 0
    _fading_in     = False
    _fading_out    = False
    _pending_scene = None
    day_cycle.init()
    tasks.reset_for_day()
    minigame_overlay.reset_all()
    scene = "start_screen"
    start_screen.init()


def _update_fade(dt):
    global _fade_alpha, _fading_in, _fading_out, _pending_scene, scene
    if _fading_in:
        _fade_alpha = min(255, _fade_alpha + int(FADE_SPEED * dt))
        if _fade_alpha >= 255:
            _fading_in  = False
            _fading_out = True
            if _pending_scene is not None:
                prev_scene  = scene
                scene = _pending_scene
                _pending_scene = None
                if scene in RESET_ON_ENTER:
                    # returning from beach fu**s shit up
                    # tasks get reset n all, so we need this ;(
                    returning_from_beach = (scene == "lighthouse" and
                                            prev_scene in _BEACH_SIDE_TRIPS)
                    if not returning_from_beach:
                        if scene in ("nightfall", "lighthouse", "day_night"):
                            minigame_overlay.reset_all()
                        SCENES[scene].init()
    elif _fading_out:
        _fade_alpha = max(0, _fade_alpha - int(FADE_SPEED * dt))
        if _fade_alpha <= 0:
            _fading_out = False


def _current_scene():
    return SCENES[scene]


def handle_event(event):
    # block all input during transitions so keypresses don't leak into the next scene
    if _fading_in or _fading_out:
        return
    # overlay wont let inputs pass if minigame active
    if minigame_overlay.handle_event(event):
        return
    _current_scene().handle_event(event)


def update(dt):
    _update_fade(dt)
    if _fading_in or _pending_scene:
        return
        
    # start screen waits for any key before the story begins
    if scene == "start_screen":
        start_screen.update(dt)
        if start_screen.done:
            switch("opening")
        return
        
    # opening is handled separately because it does not use the day cycle
    if scene == "opening":
        opening.update(dt)
        if opening.done:
            switch("beach_intro")
        return
    if scene == "beach_intro":
        animations.update(dt)
        beach_intro.update(dt)
        if beach_intro.done:
            switch("lighthouse")
        return
    
    # beach returns to day scene
    if scene == "beach":
        animations.update(dt)
        _current_scene().update(dt)
        return

    minigame_overlay.update(dt)
    if minigame_overlay.is_blocking():
        return
        
    # only tick the day clock when in day BUT not fading in or out
    if scene == "lighthouse" and not _fading_in and not _fading_out:
        day_cycle.update(dt)
        animations.update(dt)
        _current_scene().update(dt)
        if day_cycle.is_night():
            switch("nightfall")
        return

    if scene == "day_night":
        animations.update(dt)
        _current_scene().update(dt)
        if day_night.done:
            _advance_day()
        return

    if scene == "nightfall":
        # this should have fixed the bug of night starting without before fading_in is complete
        # but this didnt fix it...
        animations.update(dt)
        _current_scene().update(dt)
        if nightfall.done and not _fading_in and not _fading_out:
            _advance_day()
        return


def _advance_day():
    day_cycle.next_day()
    tasks.reset_for_day()
    for obj in day._interactables + day._visitors:
        obj.reset_daily()
        obj.on_use = None
    if day_cycle.day >= constants.DAY_NIGHT_START:
        switch("day_night")
    else:
        switch("lighthouse")


def draw(screen):
    # fill the background with the current sky color before anything else draws
    sky_color = day_cycle.sky_color()
    
    # Bugfix: If we are in the middle of switching to nightfall, keep the sky 
    # as 'day' until the fade is 100% black to prevent the visual 'pop'.
    if scene == "lighthouse" and _fading_in:
        sky_color = constants.SKY_COLORS["day"]
        
    screen.fill(sky_color)
    
    # draws non-ui elements
    _current_scene().draw(screen)

    # draws red overlay
    apply_red_overlay(screen, day_cycle.day)
    
    # draws ui elements IFFF scene != "opening" and != "start_screen"
    if scene not in ("opening", "start_screen"):
        _current_scene().draw_ui(screen)
    
    # minigame panel draws on top of everything, including UI
    minigame_overlay.draw(screen)
    
    # fade logic
    if _fade_alpha > 0:
        fade = pygame.Surface(screen.get_size())
        fade.fill((0, 0, 0))
        fade.set_alpha(_fade_alpha)
        screen.blit(fade, (0, 0))
        
def apply_red_overlay(screen, day):
    alpha = constants.RED_OVERLAY_ALPHA.get(day, 0)
    if alpha == 0:
        return
    w, h = screen.get_size()
    overlay = pygame.Surface((w, h), pygame.SRCALPHA)
    cx, cy = w // 2, h // 2
    max_r = int((cx ** 2 + cy ** 2) ** 0.5)
    # draw concentric circles from edge inward, fading to transparent at center
    steps = 48
    for i in range(steps, 0, -1):
        t = i / steps                          # 1.0 at edge, near 0 at center
        ring_alpha = int(alpha * (t ** 1.6))   # power curve — sharp edge, soft center
        r = int(max_r * t)
        pygame.draw.circle(overlay, (180, 0, 0, ring_alpha), (cx, cy), r)
    screen.blit(overlay, (0, 0))