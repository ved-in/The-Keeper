# The Keeper
**PyWeek 41 - Theme: Nightfall**

## Overview

You are the keeper of a lighthouse in a world where the sun never fully sets. The game currently starts with a cinematic opening, moves into the lighthouse/day scene, then switches into the nightfall scene once dusk hits. The current build focuses on atmosphere, dialogue presentation, and the lighthouse mood more than full gameplay content.

## Done

- Added emergency system
- Added fix_wires, log_pressure minigames
- Tasks panel for day and night
- opening at the beach - need to wire up assets
- added 3 more minigames. flip_breakers, manual_crank, pressure_valves

## To Add/Fix

- [ ] Can interact with npcs and interactables anywhere in map. Needs fix
- [ ] Beacon minigame for rhythm/timing repair
- [ ] Night scripts for day 2 and day 3
- [ ] Need removal of old night_task code. Currently only emergencies are used in night
- [ ] Need to wire up assets of fisherman, beach, sea, ships
- [ ] Need assets for interactables

## Controls

- `A / D` or `Left / Right` or `click to move`
- `Space / Enter`: advance dialogue
- `F11`: cycle display mode

## Structure

```
├── assets
│   ├── fonts
│   │   ├── IMFellEnglish-Italic.ttf
│   │   └── IMFellEnglish-Regular.ttf
│   └── sound
│       └── 33560__jobro__osd-text-9.wav
├── core
│   ├── day_cycle.py
│   ├── game.py
│   ├── __init__.py
│   ├── player.py
│   └── view.py
├── constants.py
├── main.py
├── README.md
├── requirements.txt
├── scenes
│   ├── day.py
│   ├── __init__.py
│   ├── lighthouse.py
│   ├── nightfall.py
│   └── opening.py
└── ui
    ├── dialogue.py
    ├── hud.py
    └── __init__.py
```

## Notes

- `constants.py` holds scene/dialogue config and asset paths
- `ui/dialogue.py` is used by both the opening scene and gameplay scenes
- The current flow is: `opening -> lighthouse/day -> nightfall -> next day`
