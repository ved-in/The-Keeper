import constants

# tracks how many seconds have passed in the current day
_elapsed = 0.0
day = 1


def init():
    global _elapsed, day
    _elapsed = 0.0
    day = 1


def update(dt):
    # cap at DAY_LENGTH so _elapsed never overshoots and progress never exceeds 1.0
    global _elapsed
    _elapsed = min(_elapsed + dt, constants.DAY_LENGTH)


def progress():
    # returns a value from 0.0 (start of day) to 1.0 (end of day)
    return _elapsed / constants.DAY_LENGTH


def is_night():
    # night starts when the day bar is completely full
    return progress() >= 1.0


def next_day():
    # reset the timer and increment the day counter
    global _elapsed, day
    day += 1
    _elapsed = 0.0


def sky_color():
    return constants.SKY_COLORS["night"] if is_night() else constants.SKY_COLORS["day"]