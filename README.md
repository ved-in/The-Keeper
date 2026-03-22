# The Keeper
**PyWeek 41 - Theme: Nightfall**

## Done

- [x] Main loop (`main.py`)
- [x] Scene switching (`core/game.py`)
- [x] Day/night cycle (`core/day_cycle.py`)
- [x] Player rectangle with movement and clamping (`core/player.py`)
- [x] Daytime scene (`scenes/lighthouse.py`)
- [x] Night scene (`scenes/nightfall.py`)
- [x] Dialogue box with SPACE/RETURN to advance (`ui/dialogue.py`)
- [x] HUD with day counter (`ui/hud.py`)
- [x] Night scripts per day number (`SCRIPTS` dict in nightfall)

## To Add

- [ ] Create new `scenes/lighthouse.py` for shared drawing: ground strip, tower, should be called by both day and night scenes
- [ ] Interactable objects in day scene (like a logbook)
- [ ] NPC system which triggers chat on proximity
- [ ] Beacon minigame: rhythm/timing
- [ ] Night scripts for day 2 and day 3
- [ ] Pulsing beacon glow in night scene
- [ ] `GROUND_Y` is defined seperately in `player.py` and `lighthouse.py`, need a common `constants.py`

## Structure

```
├── core
│   ├── day_cycle.py
│   ├── game.py
│   ├── __init__.py
│   └── player.py
├── main.py
├── README.md
├── requirements.txt
├── scenes
│   ├── day.py
│   ├── __init__.py
│   └── nightfall.py
└── ui
    ├── dialogue.py
    ├── hud.py
    └── __init__.py
```

## Notes

- Python 3.14 does not work with `pygame.font`. Using an older version fixes it
