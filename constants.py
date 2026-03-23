import pygame

DAY_LENGTH = 100.0  # seconds

# changes color bw day and night. can maybe add an gradient change so i made it a dict for now
SKY_COLORS = {
    "day": (62, 75, 110),
    "night": (25, 20, 45),
}

SPEED = 200
GROUND_Y = 400
ADVANCE_KEYS = (pygame.K_RETURN, pygame.K_SPACE)

#   {"x": <x_pos>, "y": <y_pos>, "label": <text_label for when close>},
INTERACTABLES = []

#   [<dialog1>, <dialog2>.... <dialogn>] must be string
# This is for interactibles. When we get close to interactibles, we can press E or X or something to interact with them
RESPONSES =[]

# index: list of dialogues
# index represents night number
SCRIPTS = {
    1: ["The beacon stutters.", "The rhythm is wrong.", "Clean the lens. The salt crust is thick."],
    2: ["A box washed ashore.", "Sealed with wax. Still warm.", "Recalibrate the mirror alignment.", "Someone left the angles wrong."],
    3: ["You hear your name.", "No one is here.", "Log the weather observations.", "Wind from the north. Temperature dropping."],
    4: ["The water is moving differently tonight.", "Replace the timing gear.", "The rhythm mechanism is worn."],
    5: ["Something surfaces.", "You do not look directly at it.", "Clear the drain channels around the base.", "The water beneath looks darker than usual."],
    6: ["A visitor left a note.", "It does not make sense.", "Inspect the foundation bolts.", "Two are loose. The rock beneath feels warmer than it should."],
    7: ["The fog smells like burning.", "Refuel the reserve tank.", "The fuel smells different today. Almost sweet."],
    8: ["The beacon lit itself tonight.", "You did not touch it.", "Replace the signal bell rope.", "The old one snapped overnight. You find no explanation."],
    9: ["The ground moved.", "The ships on the horizon are gone.", "Polish the upper lens panels."],
    10: ["Perform a full system check.", "Everything reads normal."],
}

FINISH_SCRIPTS = {
    1: ["The beam looks steadier after.", "You feel good about this."],
    2: ["The angles are correct now.", "You do not know why they were changed."],
    3: ["The log is written.", "You close the book."],
    4: ["The beacon pulses exactly right.", "You feel proud of the work."],
    5: ["The channels are clear.", "You do not look at the water on the way back up."],
    6: ["The bolts are tight.", "The structure feels solid.", "You do not mention the warmth in the log."],
    7: ["The tank is full.", "You wash your hands twice."],
    8: ["The new rope holds.", "You tie it twice to be sure."],
    9: ["The glass is clean.", "Your reflection looks wrong for a moment. You keep polishing.", "You avoid looking at your reflection again."],
    10: ["You write NOMINAL in the log. It is the last entry.", "You set down the pen.", "The lighthouse shakes."],
}

FALLBACK_NIGHT_SCRIPT = ["The night lasts longer than usual..."]

# Below  is responsible for Dialogue UI
FONT_PATH = "assets/fonts/IMFellEnglish-Regular.ttf"
PROMPT_TEXT = "SPACE / ENTER"
DEFAULT_TYPE_SOUND = "assets/sound/33560__jobro__osd-text-9.wav"
OPENING_LINES = [
    "Your grandfather built this lighthouse.",
    "Your father kept it running.",
    "Now it's your turn.",
    "The beacon keeps the ships safe.",
    "You keep the beacon running.",
    "That is enough...",
]

# these are the values that define the wider log box used in the opening
LOG_DIALOGUE = {
    "label": "KEEPER'S LOG",
    "reveal_speed": 24.0,
    "font_size": 16,
    "hint_font_size": 9,
    "side_margin": 118,
    "bottom_offset": 124,
    "height": 92,
    "shadow_y": 4,
    "corner_radius": 12,
    "accent_h": 4,
    "fade_time": 0.35,
    "max_alpha": 220,
    "tag_x": 18,
    "tag_y": 10,
    "text_x": 20,
    "text_y": 18,
    "text_y_with_label": 28,
    "text_wrap_pad": 44,
    "line_gap": 5,
    "prompt_x": 18,
    "prompt_y": 14,
    "caret_w": 3,
    "caret_trim": 6,
    "caret_x": 6,
    "caret_alpha": 160,
    "caret_speed": 8.0,
    "hint_size": 10,
    "hint_x": 16,
    "hint_y": 5,
    "hint_alpha": 150,
    "hint_speed": 6.0,
    "glow_alpha": 58,
    "text_shadow_alpha": 100,
}

# the gameplay bubble is much smaller, so its spacing lives separately
THOUGHT_DIALOGUE = {
    "font_size": 12,
    "hint_font_size": 8,
    "padding_x": 14,
    "padding_y": 10,
    "line_gap": 4,
    "safe_margin": 12,
    "tail_gap": 18,
    "max_box_w": 240,
    "extra_bottom": 8,
    "shadow_y": 4,
    "corner_radius": 16,
    "tail_inset": 18,
    "tail_mid_ratio": 0.55,
    "tail_radii": (8, 5, 3),
    "tail_head_offset": 6,
    "fallback_anchor_x": 12,
    "fallback_anchor_bottom": 84,
    "fallback_anchor_w": 24,
    "fallback_anchor_h": 40,
}

# opening.py only needs these scene-specific numbers now
OPENING_SCENE = {
    "veil": (10, 12, 20, 120),
    "pulse_start": 6.0,
    "pulse_end": 10.0,
    "glow_radius": 54,
    "glow_pulse": 16,
    "glow_alpha": 18,
    "glow_alpha_pulse": 40,
    "beacon_radius": 34,
    "beacon_pulse": 6,
    "letterbox_h": 24,
    "letterbox_ratio": 0.06,
    "fade_in": 2.0,
}

# Centralized colors for the "log" style dialogue box
LOG_COLORS = {
    "bg": (14, 14, 24),             # dark blue
    "shadow": (8, 8, 12),           # black
    "border": (96, 92, 116),        # gray
    "accent": (172, 152, 108),      # gold
    "text": (230, 225, 210),        # white
    "text_glow": (132, 126, 156),   # purple
    "tag": (176, 166, 142),         # beige
    "prompt": (150, 146, 164),      # light purple
}

# Centralized colors for the "thought" bubble style
THOUGHT_COLORS = {
    "bg": (238, 231, 214),          # light beige
    "shadow": (52, 42, 46),         # dark brown
    "border": (112, 96, 92),        # brown gray
    "text": (34, 30, 36),           # near black
    "prompt": (102, 94, 96),        # gray
}

RED_OVERLAY_ALPHA = {
    1:  0,
    2:  0,
    3:  8,
    4:  10,
    5:  10,
    6:  15,
    7:  20,
    8:  30,
    9:  40,
    10: 60,
}

VISITORS = [
    {
        "name": "Dr. Maren",
        "world_x": 300,
        "y": 360,
        "lines": {
            1: ["The perfect peace...", "The perfect quiet..."],
            2: ["That box on the rocks... I'd leave it alone."],
            "default": ["Still running tests."],
        },
    },
    {
        "name": "Old Piet",
        "world_x": 650,
        "y": 360,
        "lines": {
            1: ["Fish still bite. That's something."],
            2: ["The birds stopped singing at dawn.", "This is weird..."],
            "default": ["Hmph."],
        },
    },
]

INTERACTABLES = [
    {
        "name": "Lens",
        "world_x": 600,
        "y": 330,
        "w": 30,
        "h": 30,
        "lines": {
            1: ["The salt crust is thick.", "You clean it carefully."],
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
            1: ["You write the day's observations.", "Wind from the north."],
            "default": ["Nothing new to log."],
        },
    },
]