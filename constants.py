import pygame

DAY_LENGTH = 30.0  # seconds

# changes color bw day and night. can maybe add an gradient change so i made it a dict for now
SKY_COLORS = {
    "day": (62, 75, 110),
    "night": (25, 20, 45),
}

SPEED = 200
GROUND_Y = 400
ADVANCE_KEYS = (pygame.K_RETURN, pygame.K_SPACE)

# Below  is responsible for Dialogue UI
FONT_PATH = "assets/fonts/IMFellEnglish-Regular.ttf"
PROMPT_TEXT = "SPACE / ENTER"
DEFAULT_TYPE_SOUND = "assets/sound/33560__jobro__osd-text-9.wav"
OPENING_LINES = [
    "This lighthouse was built by your grandfather.",
    "Your father maintained it.",
    "Now it's your turn.",
    "The beacon keeps the ships safe.",
    "You keep the beacon running.",
    "That is enough...",
]

# ---------------------------------------------------------------------------
# Night intro scripts — pure player thoughts, anchor to player
# ---------------------------------------------------------------------------
SCRIPTS = {
    1: ["Sun set a bit early today.", "Better get to work."],
    2: ["Sun went down ten minutes early today.", "The shadows look... stretched."],
    3: ["The old generator is acting up.", "Got to hold it together."],
    4: ["The light is casting a strange shadow on the water.", "It almost looks like rust.", "The daylight is barely lasting six hours now."],
    5: ["The night is coming for good.", "Just keep the light spinning."],
    6: ["Everything I touch is covered in this red dust.", "The sun didn't even rise until noon today.", "I can't see the dock without the lighthouse beam hitting it."],
    7: ["I have to keep the light on.", "That's all there is."],
    8: ["It's 3 PM and it's pitch black.", "Just gotta keep the light spinning."],
    9: ["There are no boats left.", "The light is all we have."],
    10: ["The nightfall is here.", "The ground screams."],
}

# ---------------------------------------------------------------------------
# Night finish scripts — pure player thoughts shown after task completes
# ---------------------------------------------------------------------------
FINISH_SCRIPTS = {
    1: ["The lens is clear.", "The light will carry further tonight."],
    2: ["The pressure is logged.", "Numbers don't lie, even when they scare you."],
    3: ["The cables hold.", "For now."],
    4: ["The bulb is clean.", "The beam cuts through the dark like it should."],
    5: ["The sensors are in place.", "The scientist seems satisfied."],
    6: ["The shutters are locked.", "The red dust keeps falling."],
    7: ["The doors are boarded.", "This is the last supply drop."],
    8: ["The engine cools.", "The sound it made wasn't right."],
    9: ["The light keeps spinning.", "Your arms are tired.", "It doesn't matter."],
    10: ["...", "The lighthouse shakes."],
}

FALLBACK_NIGHT_SCRIPT = ["The night lasts longer than usual..."]

# ---------------------------------------------------------------------------
# Visitor dialogue — mix of plain strings (NPC only) and dicts (conversations)
# Plain strings default to speaker="npc" in dialogue.show()
# ---------------------------------------------------------------------------
VISITORS = [
    {
        "name": "Scientist",
        "world_x": 300,
        "y": 360,
        "anim_folder": "assets/characters/scientist",
        "anim_scale": 3.0,
        "y_offset": 23,
        "lines": {
            5: [
                {"speaker": "npc",
                 "text": "Excuse me, I need to deploy seismic and atmospheric sensors on your beach immediately."},
                {"speaker": "player",
                 "text": "Sure, just stay out of the lighthouse."},
                {"speaker": "npc",
                 "text": "The sun is being eclipsed by something we can't see."},
                {"speaker": "npc",
                 "text": "The red refraction index is completely unprecedented."},
                {"speaker": "npc",
                 "text": "Night is coming for good."},
            ],
            8: [
                {"speaker": "npc",
                 "text": "The readings are off the charts."},
                {"speaker": "npc",
                 "text": "The crust is fracturing because the gravity is shifting."},
                {"speaker": "npc",
                 "text": "It's 3 PM and it's pitch black."},
                {"speaker": "player",
                 "text": "Just gotta keep the light spinning."},
            ],
            9: [
                {"speaker": "npc",
                 "text": "It's pulling the magnetic field apart!"},
                {"speaker": "npc",
                 "text": "We have to leave!"},
                {"speaker": "npc",
                 "text": "The sun didn't rise at all today!"},
                {"speaker": "player",
                 "text": "There are no boats left."},
                {"speaker": "player",
                 "text": "The light is all we have."},
            ],
            10: [
                {"speaker": "npc",
                 "text": "..."},
                {"speaker": "player",
                 "text": "..."},
            ],
            "default": [
                {"speaker": "npc",
                 "text": "Still running tests."}
            ],
        },
    },
    {
        "name": "Fisherman",
        "world_x": 650,
        "y": 360,
        "lines": {
            1: [
                {"speaker": "npc",
                 "text": "Supply drop is on the dock."},
                {"speaker": "npc",
                 "text": "Sun is setting a bit early today, better get to work."},
                {"speaker": "player",
                 "text": "I'll bring them in. Thanks for the run."},
            ],
            3: [
                {"speaker": "npc",
                 "text": "You seeing this sky?"},
                {"speaker": "npc",
                 "text": "Looks like someone spilled copper in the clouds."},
                {"speaker": "npc",
                 "text": "The water feels heavy."},
                {"speaker": "player",
                 "text": "Yeah, the old generator is acting up too."},
                {"speaker": "npc",
                 "text": "Stay safe out there man, giving me the creeps."},
            ],
            7: [
                {"speaker": "npc",
                 "text": "I'm not sailing out here anymore."},
                {"speaker": "npc",
                 "text": "The water looks like blood and the engine is choking on red grit."},
                {"speaker": "npc",
                 "text": "This is my last drop."},
                {"speaker": "player",
                 "text": "I understand."},
                {"speaker": "player",
                 "text": "I have to keep the light on."},
            ],
            "default": [
                {"speaker": "npc",
                 "text": "Hmph."}
            ],
        },
    },
]

# ---------------------------------------------------------------------------
# Interactables — objects the player clicks in the world
# Plain strings here are the player examining/interacting with an object,
# so they anchor to the player by default (default_speaker="player" in handle_click)
# ---------------------------------------------------------------------------
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

# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------
DAY_TASKS = {
    1: {"interactable": "Lens", "minigame": "minigame_clean"},
}

DAY_FINISH_SCRIPTS = {
    1: ["The generator is running.", "Good enough for now."],
    2: ["Pressure logged.", "The numbers are getting worse."],
    3: ["Cables replaced.", "The light should hold another night."],
    4: ["Bulb is clean.", "The beam is as strong as it can be."],
    5: ["Sensors placed.", "The scientist seems to know something she isn't saying."],
    6: ["Shutters locked.", "The red dust gets in everywhere."],
    7: ["Doors boarded.", "Won't stop much, but it's something."],
    8: ["Engine cooled down.", "It won't last much longer."],
    9: ["Done.", "Hands are shaking."],
    10: [],
}

NIGHT_TASKS = {
    1: {"interactable": "Lens", "minigame": "minigame_clean"},
    2: {"interactable": None,   "minigame": None},
    3: {"interactable": None,   "minigame": None},
    4: {"interactable": None,   "minigame": None},
    5: {"interactable": None,   "minigame": None},
    6: {"interactable": None,   "minigame": None},
    7: {"interactable": None,   "minigame": None},
    8: {"interactable": None,   "minigame": None},
    9: {"interactable": None,   "minigame": None},
    10: {"interactable": None,  "minigame": None},
}

# ---------------------------------------------------------------------------
# UI config — these are purely visual tuning values, nothing story-related
# ---------------------------------------------------------------------------

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
