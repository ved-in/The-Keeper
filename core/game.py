import core.day_cycle as day_cycle
import scenes.lighthouse as lighthouse
import scenes.day as day
import scenes.nightfall as nightfall
import scenes.opening as opening
import core.animations as animations
import constants

import pygame

# maps scene name strings to their modules so we can switch between them easily
SCENES = {
    "opening": opening,
    "lighthouse": day,
    "nightfall": nightfall,
}

# scenes in this set get fully re-initialised every time we switch to them
RESET_ON_ENTER = {"opening", "nightfall"}

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
    # switch directly for no fade
    global scene
    scene = "opening"
    opening.init()

def switch(name):
    global _pending_scene, _fading_in
    _pending_scene = name
    _fading_in = True  # start fading to black


def _update_fade(dt):
    global _fade_alpha, _fading_in, _fading_out, _pending_scene, scene
    if _fading_in:
        _fade_alpha = min(255, _fade_alpha + int(FADE_SPEED * dt))
        if _fade_alpha >= 255:
            _fading_in = False
            _fading_out = True
            if _pending_scene is not None:
                scene = _pending_scene
                _pending_scene = None
                if scene in RESET_ON_ENTER:
                    SCENES[scene].init()
    elif _fading_out:
        _fade_alpha = max(0, _fade_alpha - int(FADE_SPEED * dt))
        if _fade_alpha <= 0:
            _fading_out = False


def _current_scene():
    return SCENES[scene]


def handle_event(event):
    _current_scene().handle_event(event)


def update(dt):
    _update_fade(dt)
    if _fading_in or _pending_scene:
        return
        
    # opening is handled separately because it does not use the day cycle
    if scene == "opening":
        opening.update(dt)
        if opening.done:
            switch("lighthouse")
        return

    day_cycle.update(dt)

    # advance all animation frames once per tick
    animations.update(dt)
    
    # when the day timer hits night threshold, switch to the night scene
    if day_cycle.is_night() and scene == "lighthouse":
        switch("nightfall")

    _current_scene().update(dt)

    # when the player finishes reading the night dialogue, start the next day
    if scene == "nightfall" and nightfall.done:
        day_cycle.next_day()
        switch("lighthouse")


def draw(screen):
    # fill the background with the current sky color before anything else draws
    screen.fill(day_cycle.sky_color())
    
    # draws non-ui elements
    _current_scene().draw(screen)

    # draws red overlay
    apply_red_overlay(screen, day_cycle.day)
    
    # draws ui elements IFFF scene != "opening"
    if scene != "opening":
        _current_scene().draw_ui(screen)
    
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
    overlay = pygame.Surface(screen.get_size())
    overlay.fill((255, 0, 0))
    overlay.set_alpha(alpha)
    screen.blit(overlay, (0, 0))