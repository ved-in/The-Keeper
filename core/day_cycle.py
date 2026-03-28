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
    if is_night():
        return constants.SKY_COLORS["night"]
    
    day_colors = constants.DAY_SKY_COLORS
    base = day_colors.get(day, constants.SKY_COLORS["day"])
    
    # blend slightly to next day's color
    next_col = day_colors.get(day + 1, base)
    t = progress()
    r = int(base[0] + (next_col[0] - base[0]) * t * 0.4)
    g = int(base[1] + (next_col[1] - base[1]) * t * 0.4)
    b = int(base[2] + (next_col[2] - base[2]) * t * 0.4)
    return (r, g, b)