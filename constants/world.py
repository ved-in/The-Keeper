DAY_LENGTH = 30.0  # seconds

SPEED    = 200
GROUND_Y = 400

SKY_COLORS = {
    "day":   (62, 75, 110),
    "night": (25, 20, 45),
}

INTERACTABLES = [
    {
        "name": "Lens",
        "world_x": 600,
        "y": 330,
        "w": 30,
        "h": 30,
        "lines": {
            1:         ["The salt crust is thick.", "You clean it carefully."],
            "default": ["The lens is clean."],
        },
    },
    {
        "name": "Logbook",
        "world_x": 200,
        "y": 350,
        "w": 24,
        "h": 30,
        "lines": {
            2:         ["The barometer reads low.", "You should log it."],
            "default": ["Nothing new to log."],
        },
    },
    {
        "name": "Generator",
        "world_x": -200,
        "y": 370,
        "w": 36,
        "h": 34,
        "lines": {
            1:         ["The generator hums unevenly.", "The wires are frayed."],
            3:         ["The cables look worse.", "Better replace them now."],
            "default": ["The generator is running."],
        },
    },
    {
        "name": "Breaker Box",
        "world_x": -400,
        "y": 350,
        "w": 28,
        "h": 36,
        "lines": {
            "default": ["The breaker panel is mounted to the wall.", "Some switches look tripped."],
        },
    },
    {
        "name": "Engine",
        "world_x": -300,
        "y": 370,
        "w": 40,
        "h": 32,
        "lines": {
            8:         ["The engine is running hot.", "The pipes are shaking."],
            "default": ["The engine rumbles steadily."],
        },
    },
    {
        "name": "Light Motor",
        "world_x": 500,
        "y": 320,
        "w": 28,
        "h": 28,
        "lines": {
            9:         ["The motor is failing.", "You'll have to crank it by hand."],
            "default": ["The light motor spins steadily."],
        },
    },
]

LIGHTHOUSE_DOOR = {
    "world_x": 450,
    "y":        360,
    "w":        28,
    "h":        44,
}