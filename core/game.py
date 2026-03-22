import core.day_cycle as day_cycle
import scenes.lighthouse as lighthouse
import scenes.day as day
import scenes.nightfall as nightfall
import scenes.opening as opening
import core.animations as animations

# maps scene name strings to their modules so we can switch between them easily
SCENES = {
    "opening": opening,
    "lighthouse": day,
    "nightfall": nightfall,
}

# scenes in this set get fully re-initialised every time we switch to them
RESET_ON_ENTER = {"opening", "nightfall"}

scene = "opening"


def init():
    day_cycle.init()
    lighthouse.init()
    day.init()
    # load all sprite sheets before the game loop starts
    animations.load_all()
    switch("opening")


def switch(name):
    global scene
    scene = name
    # reset scenes that need a clean slate each time they are entered
    if name in RESET_ON_ENTER:
        SCENES[name].init()


def _current_scene():
    return SCENES[scene]


def handle_event(event):
    _current_scene().handle_event(event)


def update(dt):
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
    _current_scene().draw(screen)
