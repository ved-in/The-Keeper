# The Keeper

**PyWeek 41 - Theme: Nightfall**

## Overview

You are the keeper of a lighthouse in a world where the sun never fully sets. The game currently starts with a cinematic opening, moves into the lighthouse/day scene, then switches into the nightfall scene once dusk hits. The current build focuses on atmosphere, dialogue presentation, and the lighthouse mood more than full gameplay content.

## Done

- Game is playable now with full 10 days. Emergencies occur at night
- At day 6, day and night will be merged to one, emergencies can occur

## To Add/Fix

- [ ] Need assets for interactables

## Controls

- `A / D` or `Left / Right` or `click to move`
- `Space / Enter`: advance dialogue
- `F11`: cycle display mode

## Structure

```bash
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
- rudy is doing the voice acting and soundwork because no one else can 🥀

## Contributors

- ved-in - primary developer (core architecture, game mechanics, implementation)
- X3r0Day - secondary developer
- RudyDaBot - voice acting and sound design
- xodo2fast4u - original concept and storyline contributions
- omnimistic - storyline direction
