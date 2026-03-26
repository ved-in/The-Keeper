import pygame

ADVANCE_KEYS = (pygame.K_RETURN, pygame.K_SPACE)

DAY_TASKS = {
    1:  [{"interactable": "Lens", "minigame": "minigame_clean"},
        {"interactable": "Generator", "minigame": "minigame_wires"}],
    2:  [{"interactable": "Logbook", "minigame": "minigame_pressure"}],
    3:  [{"interactable": "Generator", "minigame": "minigame_wires"},
        {"interactable": "Logbook", "minigame": "minigame_pressure"}],
    4:  [{"interactable": "Lens", "minigame": "minigame_clean"}],
    5:  [],
    6:  [],
    7:  [],
    8:  [],
    9:  [],
    10: [],
}

NIGHT_TASKS = {
    1:  [{"interactable": "Lens", "minigame": "minigame_clean"}],
    2:  [],
    3:  [],
    4:  [],
    5:  [],
    6:  [],
    7:  [],
    8:  [],
    9:  [],
    10: [],
}
