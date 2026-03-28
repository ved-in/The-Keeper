import constants

_day_tasks_done = {}
_night_tasks_done = {}


def _normalise(entry) -> list[dict]:
    if entry is None:
        return []
    if isinstance(entry, dict):
        return [entry]
    return list(entry)


def reset_for_day():
    global _day_tasks_done
    tasks = _normalise(constants.DAY_TASKS.get(_current_day()))
    _day_tasks_done = {_task_id(task, i): False for i, task in enumerate(tasks)}
def reset_for_night():
    global _night_tasks_done
    tasks = _normalise(constants.NIGHT_TASKS.get(_current_day()))
    _night_tasks_done = {_task_id(task, i): False for i, task in enumerate(tasks)}

def get_day_tasks(day: int) -> list[dict]:
    return _normalise(constants.DAY_TASKS.get(day))
def get_night_tasks(day: int) -> list[dict]:
    return _normalise(constants.NIGHT_TASKS.get(day))


def day_task_done(idx: int = 0) -> bool:
    return _day_tasks_done.get(idx, True)
def night_task_done(idx: int = 0) -> bool:
    return _night_tasks_done.get(idx, True)


def all_day_tasks_done() -> bool:
    return all(_day_tasks_done.values()) if _day_tasks_done else True
def all_night_tasks_done() -> bool:
    return all(_night_tasks_done.values()) if _night_tasks_done else True

def any_night_minigames(day: int) -> bool:
    return any(t.get("minigame") for t in get_night_tasks(day))


def complete_day_task(idx: int = 0):
    global _day_tasks_done
    if idx in _day_tasks_done:
        _day_tasks_done[idx] = True
def complete_night_task(idx: int = 0):
    global _night_tasks_done
    if idx in _night_tasks_done:
        _night_tasks_done[idx] = True


def _task_id(task: dict, fallback_idx: int) -> int:
    return int(task.get("idx", fallback_idx))


def _current_day() -> int:
    import core.day_cycle as day_cycle
    return day_cycle.day
