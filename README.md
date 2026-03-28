# The Keeper

**PyWeek 41 - Theme: Nightfall**

## Overview

You are the keeper of a lighthouse in a world where the sun never fully sets. The game currently starts with a cinematic opening, moves into the lighthouse/day scene, then switches into the nightfall scene once dusk hits. The current build focuses on atmosphere, dialogue presentation, and the lighthouse mood more than full gameplay content.

## Done

- Game is playable now with full 10 days. Emergencies occur at night
- At day 6, day and night will be merged to one, emergencies can occur

## To Add/Fix

- [ ] Need fixing of storyline at many points

## Controls

- `A / D` or `Left / Right` or `click to move`
- `Space / Enter`: advance dialogue
- `F11`: cycle display mode

## Structure

```bash
.
├── assets
│   ├── book
│   ├── breaker
│   ├── characters
│   ├── credits
│   ├── fonts
│   ├── generator
│   ├── map
│   ├── rug
│   ├── sound
│   └── sprites
├── constants
│   ├── assets.py
│   ├── dialogue.py
│   ├── gameplay.py
│   ├── sounds.py
│   ├── ui.py
│   └── world.py
├── core
│   ├── day_cycle.py
│   ├── game.py
│   ├── inside_lh.py
│   ├── save.py
│   ├── sound.py
│   └── view.py
├── entities
│   ├── animations.py
│   ├── interactables.py
│   ├── player.py
│   └── visitors.py
├── minigames
│   ├── clean_lens.py
│   ├── fix_wires.py
│   ├── flip_breakers.py
│   ├── log_pressure.py
│   ├── lubricate_engine.py
│   ├── manual_crank.py
│   ├── pressure_valves.py
│   └── refuel_generator.py
├── scenes
│   ├── beach.py
│   ├── beach_intro.py
│   ├── day.py
│   ├── day_night.py
│   ├── lighthouse.py
│   ├── nightfall.py
│   ├── opening.py
│   └── start_screen.py
├── systems
│   ├── emergency.py
│   ├── minigame.py
│   ├── minigame_overlay.py
│   ├── neglect.py
│   └── tasks.py
├── ui
│   ├── dialogue.py
│   ├── hud.py
│   └── pause_menu.py
├── LICENSE
├── main.py
├── README.md
└── requirements.txt
```

## Notes

- `constants/` holds asset paths, dialogue scripts, gameplay tuning, UI config, and world data
- `ui/dialogue.py` is shared by the opening, beach intro, and gameplay scenes
- The current flow is: `start_screen -> opening -> beach_intro -> lighthouse/day -> beach or nightfall`, with `day_night` taking over in later days
- rudy is doing the voice acting and soundwork because no one else can 🥀

## Contributors

- ved-in - primary developer (core architecture, game mechanics, implementation)
- X3r0Day - secondary developer
- RudyDaBot - voice acting and sound design
- xodo2fast4u - original concept and storyline contributions
- omnimistic - storyline direction
