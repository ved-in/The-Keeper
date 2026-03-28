import pygame

ADVANCE_KEYS = (pygame.K_RETURN, pygame.K_SPACE)

BEACH_DAYS = {5}
DAY_NIGHT_START = 6

DAY_SKY_COLORS = {
    1:  (62,  75,  110),
    2:  (58,  70,  108),
    3:  (70,  62,  100),
    4:  (80,  58,   90),
    5:  (88,  55,   80),
    6:  (90,  50,   60),
    7:  (80,  40,   45),
    8:  (70,  30,   30),
    9:  (55,  20,   20),
    10: (40,  10,   10),
}

# Interactable name shown to player per day: overrides default lines
# (narrative framing for reused minigames)
INTERACTABLE_FLAVOUR = {
    # (day, interactable_name): lines
    (3, "Generator"):  ["The cable conduits are badly frayed.", "You rewire them carefully."],
    (4, "Engine"):     ["The pressure valves are screaming.", "You vent them before something bursts."],
    (8, "Breaker Box"):["Half the breakers have tripped again.", "You reset them one by one."],
}

DAY_TASKS = {
    1: [
        {"interactable": "Generator",  "minigame": "minigame_wires",    "idx": 0, "label": "Fix Generator Wiring"},
        {"interactable": "Lens",       "minigame": "minigame_clean",    "idx": 1, "label": "Clean the Lens"},
        {"interactable": "Breaker Box","minigame": "minigame_breakers", "idx": 2, "label": "Flip the Breakers"},
    ],
    2: [
        {"interactable": "Logbook",    "minigame": "minigame_pressure", "idx": 0, "label": "Log Pressure"},
    ],
    3: [
        {"interactable": "Generator",  "minigame": "minigame_wires",    "idx": 0, "label": "Replace Frayed Cables"},
        {"interactable": "Logbook",    "minigame": "minigame_pressure", "idx": 1, "label": "Log Pressure"},
        {"interactable": "Lens",       "minigame": "minigame_clean",    "idx": 2, "label": "Clean the Lens"},
    ],
    4: [
        {"interactable": "Lens",       "minigame": "minigame_clean",    "idx": 0, "label": "Clean the Lens"},
        {"interactable": "Engine",     "minigame": "minigame_valves",   "idx": 1, "label": "Vent Engine Pressure"},
    ],
    5: [
        {"interactable": "Engine",     "minigame": "minigame_lube",     "idx": 0, "label": "Lubricate Engine"},
        {"interactable": "Lens",       "minigame": "minigame_clean",    "idx": 1, "label": "Clean the Lens"},
        {"task_type": "beach",                                          "idx": 2, "label": "Assist Scientist"},
    ],
    6: [
        {"interactable": "Lens",       "minigame": "minigame_clean",    "idx": 0, "label": "Clean the Lens"},
        {"interactable": "Logbook",    "minigame": "minigame_pressure", "idx": 1, "label": "Log Pressure"},
    ],
    7: [
        {"interactable": "Generator",  "minigame": "minigame_refuel",   "idx": 1, "label": "Refuel Generator"},
        {"task_type": "board_door",                                     "idx": 2, "label": "Board Up Lower Doors"},
        {"interactable": "Lens",       "minigame": "minigame_clean",    "idx": 3, "label": "Clean the Lens"},
    ],
    8: [
        {"interactable": "Engine",     "minigame": "minigame_valves",   "idx": 0, "label": "Vent Engine Pressure"},
        {"interactable": "Lens",       "minigame": "minigame_clean",    "idx": 1, "label": "Clean the Lens"},
        {"interactable": "Breaker Box","minigame": "minigame_breakers", "idx": 2, "label": "Reset Breakers"},
    ],
    9: [
        {"interactable": "Light Motor","minigame": "minigame_crank",    "idx": 0, "label": "Crank the Light"},
        {"interactable": "Lens",       "minigame": "minigame_clean",    "idx": 1, "label": "Clean the Lens"},
    ],
    10: [
        {"task_type": "survive",                                        "idx": 0, "label": "Survive"},
    ],
}

NIGHT_TASKS = {k: [] for k in range(1, 11)}
NIGHT_TASKS[1] = [{"interactable": "Lens", "minigame": "minigame_clean"}]
