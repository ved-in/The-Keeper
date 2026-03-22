# The Keeper
**PyWeek 41 - Theme: Nightfall**

## Overview

You are the keeper of a lighthouse in a world where the sun never fully sets. The game currently starts with a cinematic opening, moves into the lighthouse/day scene, then switches into the nightfall scene once dusk hits. The current build focuses on atmosphere, dialogue presentation, and the lighthouse mood more than full gameplay content.

## Done

- [x] Main loop (`main.py`)
- [x] Scene switching (`core/game.py`)
- [x] Day/night cycle (`core/day_cycle.py`)
- [x] Player rectangle with movement and clamping (`core/player.py`)
- [x] Lighthouse/day scene (`scenes/day.py`)
- [x] Shared lighthouse drawing (`scenes/lighthouse.py`)
- [x] Night scene (`scenes/nightfall.py`)
- [x] Opening cinematic scene (`scenes/opening.py`)
- [x] Shared dialogue system with styled log/thought layouts (`ui/dialogue.py`)
- [x] HUD with day counter (`ui/hud.py`)
- [x] Pulsing beacon glow in night scene
- [x] Opening typewriter text with typing sound
- [x] Custom font support from `assets/fonts`
- [x] Fixed display modes with `F11`: windowed, borderless, fullscreen
- [x] Viewport scaling helper for consistent framing across display modes (`core/view.py`)
- [x] Ground now has texture
- [x] Added animations for entities `core/animations.py`
- [x] Fixed bug where night started before the timer gets full

## To Add

- [ ] Interactable objects in day scene (logbook, maintenance table, etc.)
- [ ] NPC system with proximity-triggered conversations
- [ ] Beacon minigame for rhythm/timing repair
- [ ] Night scripts for day 2 and day 3
- [ ] Daytime maintenance tasks with feedback/state changes

## Controls

- ~~`A / D` or `Left / Right`: move~~ click to move
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
