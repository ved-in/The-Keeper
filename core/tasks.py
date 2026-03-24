import constants

_day_task_done   = False
_night_task_done = False


def reset_for_day():
    global _day_task_done
    _day_task_done = False


def reset_for_night():
    global _night_task_done
    _night_task_done = False


def day_task_done() -> bool:
    return _day_task_done


def night_task_done() -> bool:
    return _night_task_done


def get_night_minigame(day: int) -> str | None:
    task = constants.NIGHT_TASKS.get(day)
    if task is None:
        return None
    return task.get("minigame")


def get_day_minigame(day: int) -> str | None:
    task = constants.DAY_TASKS.get(day)
    if task is None:
        return None
    return task.get("minigame")


def complete_day_task():
    global _day_task_done
    _day_task_done = True


def complete_night_task():
    global _night_task_done
    _night_task_done = True