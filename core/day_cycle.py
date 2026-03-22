import constants

_elapsed = 0.0
day = 1


def init():
    global _elapsed, day
    _elapsed = 0.0
    day = 1


def update(dt):
    global _elapsed
    _elapsed = min(_elapsed + dt, constants.DAY_LENGTH)


def progress():
    return _elapsed / constants.DAY_LENGTH


def is_night():
    return progress() >= 0.75


def next_day():
    global _elapsed, day
    day += 1
    _elapsed = 0.0


def sky_color():
    return constants.SKY_COLORS["night"] if is_night() else constants.SKY_COLORS["day"]