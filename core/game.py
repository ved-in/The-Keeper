import core.day_cycle as day_cycle
import core.sound as sound
import core.save as save
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
import systems.neglect as neglect
import ui.dialogue as dialogue
import ui.pause_menu as pause_menu
import constants
import pygame

SCENES = {
    "start_screen": start_screen,
    "opening":      opening,
    "beach_intro":  beach_intro,
    "lighthouse":   day,
    "day_night":    day_night,
    "nightfall":    nightfall,
    "beach":        beach,
}

RESET_ON_ENTER    = {"start_screen", "opening", "beach_intro", "nightfall", "lighthouse", "day_night", "beach"}
_BEACH_SIDE_TRIPS = {"beach"}
_NO_PAUSE_SCENES  = {"start_screen", "opening", "beach_intro"}

scene           = "opening"
_fade_alpha     = 0
_fading_in      = False
_fading_out     = False
_pending_scene  = None
FADE_SPEED      = 200


def init():
    day_cycle.init()
    sound.init()
    pause_menu.init()
    neglect.reset()
    lighthouse.init()
    day.init()
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

    global scene
    scene = "start_screen"
    start_screen.init()


def switch(name):
    global _pending_scene, _fading_in
    _pending_scene = name
    _fading_in = True


def skip_to_night():
    global _pending_scene, _fading_in
    _pending_scene = "nightfall"
    _fading_in = True


def _do_save():
    save.save(
        day              = day_cycle.day,
        elapsed          = day_cycle._elapsed,
        scene            = scene,
        day_tasks_done   = tasks._day_tasks_done,
        night_tasks_done = tasks._night_tasks_done,
    )


def _do_load(data: dict):
    day_cycle.day           = data["day"]
    day_cycle._elapsed      = data["elapsed"]
    tasks._day_tasks_done   = data["day_tasks_done"]
    tasks._night_tasks_done = data["night_tasks_done"]
    tasks._tasks_day        = data["day"]


def restart(new_game: bool = False):
    global scene, _fade_alpha, _fading_in, _fading_out, _pending_scene
    if new_game:
        save.delete()
    _fade_alpha    = 0
    _fading_in     = False
    _fading_out    = False
    _pending_scene = None
    pause_menu.close()
    sound.stop_all()
    day_cycle.init()
    neglect.reset()
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
                prev_scene     = scene
                scene          = _pending_scene
                _pending_scene = None
                if scene in RESET_ON_ENTER:
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


def _can_pause() -> bool:
    return (scene not in _NO_PAUSE_SCENES and
            not _fading_in and not _fading_out and
            not minigame_overlay.is_blocking())


def handle_event(event):
    if neglect.handle_event(event):
        return
    if _fading_in or _fading_out:
        return
    if _can_pause() or pause_menu.is_active():
        if pause_menu.handle_event(event, on_quit_to_menu=_on_quit_to_menu):
            return
    if minigame_overlay.handle_event(event):
        return
    _current_scene().handle_event(event)


def _on_quit_to_menu():
    _do_save()
    restart(new_game=False)


def update(dt):
    _update_fade(dt)
    if neglect.failed():
        neglect.update(dt)
        return
    if _fading_in or _pending_scene:
        return
    if pause_menu.is_active():
        return

    if scene == "start_screen":
        start_screen.update(dt)
        if start_screen.done:
            if save.has_save():
                data = save.load()
                if data:
                    _do_load(data)
                    sound.start_day(day_cycle.day)
                    switch(data["scene"])
                else:
                    switch("opening")
            else:
                switch("opening")
        return

    if scene == "opening":
        opening.update(dt)
        if opening.done:
            switch("beach_intro")
        return

    if scene == "beach_intro":
        animations.update(dt)
        beach_intro.update(dt)
        if beach_intro.done:
            sound.start_day(day_cycle.day)
            switch("lighthouse")
        return

    if scene == "beach":
        animations.update(dt)
        _current_scene().update(dt)
        return

    minigame_overlay.update(dt)
    if minigame_overlay.is_blocking():
        return

    if scene == "lighthouse" and not _fading_in and not _fading_out:
        if not dialogue.active():
            day_cycle.update(dt)
        animations.update(dt)
        _current_scene().update(dt)
        if neglect.failed():
            return
        if day_cycle.is_night():
            _apply_missed_task_penalty(
                "Too much daylight work was left unfinished. The light goes dark before night truly begins."
            )
            if neglect.failed():
                return
            switch("nightfall")
        return

    if scene == "day_night":
        animations.update(dt)
        _current_scene().update(dt)
        if neglect.failed():
            return
        if day_night.done:
            _apply_missed_task_penalty(
                "The chores pile up faster than you can answer them. The light finally gives way."
            )
            if neglect.failed():
                return
            _advance_day()
        return

    if scene == "nightfall":
        animations.update(dt)
        _current_scene().update(dt)
        if neglect.failed():
            return
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
        sound.start_day(day_cycle.day)
        switch("day_night")
    else:
        sound.start_day(day_cycle.day)
        switch("lighthouse")


def draw(screen):
    sky_color = day_cycle.sky_color()
    if scene == "lighthouse" and _fading_in:
        sky_color = constants.SKY_COLORS["day"]
    screen.fill(sky_color)
    _current_scene().draw(screen)
    apply_red_overlay(screen, day_cycle.day)
    if scene not in ("opening", "start_screen"):
        _current_scene().draw_ui(screen)
    minigame_overlay.draw(screen)
    neglect.draw_overlay(screen)
    if _fade_alpha > 0:
        fade = pygame.Surface(screen.get_size())
        fade.fill((0, 0, 0))
        fade.set_alpha(_fade_alpha)
        screen.blit(fade, (0, 0))
    pause_menu.draw(screen)


def apply_red_overlay(screen, day):
    alpha = constants.RED_OVERLAY_ALPHA.get(day, 0)
    if alpha == 0:
        return
    w, h    = screen.get_size()
    overlay = pygame.Surface((w, h), pygame.SRCALPHA)
    cx, cy  = w // 2, h // 2
    max_r   = int((cx ** 2 + cy ** 2) ** 0.5)
    steps   = 48
    for i in range(steps, 0, -1):
        t          = i / steps
        ring_alpha = int(alpha * (t ** 1.6))
        r          = int(max_r * t)
        pygame.draw.circle(overlay, (180, 0, 0, ring_alpha), (cx, cy), r)
    screen.blit(overlay, (0, 0))


def handle_resize():
    animations.rebuild_scaled()
    lighthouse.rebuild_scaled()
    beach_intro.rebuild_scaled()


def _apply_missed_task_penalty(reason: str) -> None:
    missed = 0
    for i, task in enumerate(tasks.get_day_tasks(day_cycle.day)):
        if task.get("task_type") == "survive":
            continue
        if not tasks.day_task_done(task.get("idx", i)):
            missed += 1
    if missed:
        neglect.add(constants.NEGLECT_DAY_END_PENALTY * missed, reason)
