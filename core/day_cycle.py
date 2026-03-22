DAY_LENGTH = 10.0  # seconds

_elapsed = 0.0
day = 1

# changes color bw day and night. can maybe add an gradient change so i made it a dict for now
SKY_COLORS = {
    "day": (62, 75, 110),
    "night": (25, 20, 45),
}


def init():
    global _elapsed, day
    _elapsed = 0.0
    day = 1


def update(dt):
    global _elapsed
    _elapsed = min(_elapsed + dt, DAY_LENGTH)


def progress():
    return _elapsed / DAY_LENGTH


def is_night():
    return progress() >= 0.75


def next_day():
    global _elapsed, day
    day += 1
    _elapsed = 0.0


def sky_color():
    return SKY_COLORS["night"] if is_night() else SKY_COLORS["day"]