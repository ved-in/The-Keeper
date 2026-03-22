import core.day_cycle as day_cycle
import scenes.day as day
import scenes.nightfall as nightfall

scene = "lighthouse"


def init():
    day_cycle.init()
    day.init()
    nightfall.init()


def switch(name):
    global scene
    scene = name


def handle_event(event):
    if scene == "lighthouse":
        day.handle_event(event)
    elif scene == "nightfall":
        nightfall.handle_event(event)


def update(dt):
    day_cycle.update(dt)

    if day_cycle.is_night() and scene == "lighthouse":
        switch("nightfall")
        
    if scene == "lighthouse":
        day.update(dt)
    elif scene == "nightfall":
        nightfall.update(dt)
        if nightfall.done:
            nightfall.done = False
            day_cycle.next_day()
            switch("lighthouse")


def draw(screen):
    screen.fill(day_cycle.sky_color())
    
    # depending on which scene it is, it draws corresponding scene
    if scene == "lighthouse":
        day.draw(screen)
    elif scene == "nightfall":
        nightfall.draw(screen)
        