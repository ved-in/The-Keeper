DAY_LENGTH = 120.0  # seconds

SPEED    = 300
GROUND_Y = 400

SKY_COLORS = {
    "day":   (62, 75, 110),
    "night": (25, 20, 45),
}

INTERACTABLES = [
    {
        "name": "Lens",
        "world_x": 480,
        "y": 170,
        "w": 15,
        "h": 15,
        "lines": {
            1:         ["The salt crust is thick.", "You clean it carefully."],
            "default": ["The lens is clean."],
        },
    },
    {
        "name": "Logbook",
        "world_x": 200,
        "y": 375,
        "w": 24,
        "h": 30,
        "lines": {
            2:         ["The barometer reads low.", "You should log it."],
            "default": ["Nothing new to log."],
        },
        "anim_path": "assets/book",
        "anim_scale": 0.3,
    },
    {
        "name": "Generator",
        "world_x": -120,
        "y": 370,
        "w": 70,
        "h": 70,
        "lines": {
            1:         ["The generator hums unevenly.", "The wires are frayed."],
            3:         ["The cables look worse.", "Better replace them now."],
            "default": ["The generator is running."],
        },
    },
    {
        "name": "Breaker Box",
        "world_x": 450,
        "y": 370,
        "w": 20,
        "h": 20,
        "lines": {
            "default": ["The breaker panel is mounted to the wall.", "Some switches look tripped."],
        },
    },
    {
        "name": "Engine",
        "world_x": -190,
        "y": 380,
        "w": 40,
        "h": 40,
        "lines": {
            8:         ["The engine is running hot.", "The pipes are shaking."],
            "default": ["The engine rumbles steadily."],
        },
    },
    {
        "name": "Light Motor",
        "world_x": 480,
        "y": 250,
        "w": 28,
        "h": 28,
        "lines": {
            9:         ["The motor is failing.", "You'll have to crank it by hand."],
            "default": ["The light motor spins steadily."],
        },
    },
]

LIGHTHOUSE_DOOR = {
    "world_x": 480,
    "y":        380,
    "w":        20,
    "h":        30,
}
