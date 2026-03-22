import core.day_cycle as day_cycle
import scenes.lighthouse as lighthouse
import scenes.day as day
import scenes.nightfall as nightfall
import scenes.opening as opening

SCENES = {
    "opening": opening,
    "lighthouse": day,
    "nightfall": nightfall,
}
RESET_ON_ENTER = {"opening", "nightfall"}
scene = "opening"


def init():
    day_cycle.init()
    lighthouse.init()
    day.init()
    switch("opening")


def switch(name):
    global scene
    scene = name
    if name in RESET_ON_ENTER:
        SCENES[name].init()


def _current_scene():
    return SCENES[scene]


def handle_event(event):
    _current_scene().handle_event(event)


def update(dt):
    if scene == "opening":
        opening.update(dt)
        if opening.done:
            switch("lighthouse")
        return

    day_cycle.update(dt)

    if day_cycle.is_night() and scene == "lighthouse":
        switch("nightfall")

    _current_scene().update(dt)

    if scene == "nightfall" and nightfall.done:
        day_cycle.next_day()
        switch("lighthouse")


def draw(screen):
    screen.fill(day_cycle.sky_color())
    _current_scene().draw(screen)
