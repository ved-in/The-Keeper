OPENING_LINES = [
    "This lighthouse was built by your grandfather.",
    "Your father maintained it.",
    "Now it's your turn.",
    "The beacon keeps the ships safe.",
    "You keep the beacon running.",
    "That is enough...",
]

DAY_START_SCRIPTS = {
    1: [
        "First things first.",
        "Most of the work is done outside. I do not need to enter the lighthouse interior.",
        "I can move with A and D, or click where I want to walk.",
        "The highlighted machinery marks what still needs attention.",
        "If I let chores pile up, the Neglect meter will start to climb.",
    ],
}

# Player thoughts shown at the start of each night
SCRIPTS = {
    2:  ["Sun went down ten minutes early today.", "The shadows look... stretched."],
    4:  ["The light is casting a strange shadow on the water.", "It almost looks like rust.", "The daylight is barely lasting six hours now."],
    6:  ["Everything I touch is covered in this red dust.", "The sun didn't even rise until noon today.", "I can't see the dock without the lighthouse beam hitting it."],
}
FALLBACK_NIGHT_SCRIPT = ["The day lasted shorter yet again..."]

NIGHT_TUTORIAL_SCRIPTS = {
    1: [
        "Night comes quickly now.",
        "If something fails, the red alert will point me to the problem.",
        "I only need to keep the lighthouse operating until dawn.",
        "If I ignore a failure too long, the Neglect meter will surge.",
    ],
}

DAY_NIGHT_TUTORIAL_SCRIPTS = {
    6: [
        "There is no clean break between day and night anymore.",
        "The chores keep coming, and emergencies can interrupt them at any time.",
        "If the work stacks up, the Neglect meter will keep rising.",
    ],
}

# Shown after each night
FINISH_SCRIPTS = {
    1:  ["The another night...", "The light will carry further tonight."],
    2:  ["The pressure has increased...", "This is worrisome", "Numbers don't lie, even when they scare you."],
    3:  ["The cables hold and the lens shines.", "For now."],
    4:  ["The bulb is clean, but the pressure is building up.", "The beam cuts through the dark like it should."],
    5:  ["The sensors had been placed.", "The scientist seems satisfied and worried at the same time.", "Weird.."],
    6:  ["The shutters are locked.", "The red dust keeps falling.", "What in tarnation is this??"],
    7:  ["The doors are boarded.", "This is the last supply drop.", "Better make this count."],
    8:  ["The engine cools.", "The sound it made wasn't right.", "Its all that red dust's doing."],
    9:  ["The light keeps spinning.", "Your arms are tired.", "Your arms don't matter.", "The light must go on."],
    10: ["...", "The lighthouse shakes."],
}

# Shown after completing all day tasks
DAY_FINISH_SCRIPTS = {
    1:  ["Everything seems functional.", "Good enough for now."],
    2:  ["Pressure logged.", "The numbers are getting worse."],
    3:  ["Pressure seems to be stabilizing but that Generator is worrying me.", "The light should hold another night."],
    4:  ["Bulb is clean.", "Engine is strong.","The beam is as strong as it can be."],
    5:  ["Sensors placed.", "The scientist seems to know something and he isn't saying it.", "I don't like secrets..."],
    6:  ["Shutters locked.", "The red dust gets in everywhere.", "At this rate ill get asthma.."],
    7:  ["Doors boarded.", "Won't stop much, but it's something."],
    8:  ["The Engine cooled down.", "It won't last much longer."],
    9:  ["Done.", "My hands are shaking.", "I cannot bear this"],
    10: [],
}

VISITORS = [
    {
        "name": "Scientist",
        "world_x": 300,
        "y": 360,
        "anim_folder": "assets/characters/scientist",
        "anim_scale": 3.0,
        "y_offset": 43,
        "lines": {
            5: [
                {"text": "Excuse me, I need to deploy seismic and atmospheric sensors on your beach immediately.", "speaker": "npc"},
                {"text": "Sure, just stay out of the lighthouse.", "speaker": "player"},
                {"text": "The sun is being eclipsed by something we can't see.", "speaker": "npc"},
                {"text": "The red refraction index is completely unprecedented.", "speaker": "npc"},
                {"text": "Night is coming for good.", "speaker": "npc"},
            ],
            8: [
                {"text": "The readings are off the charts.", "speaker": "npc"},
                {"text": "The crust is fracturing because the gravity is shifting.", "speaker": "npc"},
                {"text": "It's 3 PM and it's pitch black.", "speaker": "npc"},
                {"text": "Just gotta keep the light spinning.", "speaker": "player"},
            ],
            9: [
                {"text": "It's pulling the magnetic field apart!", "speaker": "npc"},
                {"text": "We have to leave!", "speaker": "npc"},
                {"text": "The sun didn't rise at all today!", "speaker": "npc"},
                {"text": "There are no boats left.", "speaker": "player"},
                {"text": "The light is all we have.", "speaker": "player"},
            ],
            10: [
                {"text": "...", "speaker": "npc"},
                {"text": "...", "speaker": "player"},
            ],
            "default": ["Still running tests."],
        },
    },
    {
        "name": "Fisherman",
        "world_x": 680,
        "y": 350,
        "anim_folder": "assets/characters/fisherman/idle",
        "anim_scale": 2.2,
        "y_offset": 40,
        "lines": {
            1: [
                {"text": "Supply drop is on the dock.", "speaker": "npc"},
                {"text": "Sun is setting a bit early today, better get to work.", "speaker": "npc"},
                {"text": "I'll bring them in. Thanks for the run.", "speaker": "player"},
            ],
            3: [
                {"text": "You seeing this sky?", "speaker": "npc"},
                {"text": "Looks like someone spilled copper in the clouds.", "speaker": "npc"},
                {"text": "The water feels heavy.", "speaker": "npc"},
                {"text": "Yeah, the old generator is acting up too.", "speaker": "player"},
                {"text": "Stay safe out there man, giving me the creeps.", "speaker": "npc"},
            ],
            7: [
                {"text": "I'm not sailing out here anymore.", "speaker": "npc"},
                {"text": "The water looks like blood and the engine is choking on red grit.", "speaker": "npc"},
                {"text": "This is my last drop.", "speaker": "npc"},
                {"text": "I understand...", "speaker": "player"},
                {"text": "Take care...", "speaker": "player"},
                {"text": "I have to keep the light on.", "speaker": "player"},
            ],
            "default": ["The fish aint bitin eh?"],
        },
    },
]
