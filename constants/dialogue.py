OPENING_LINES = [
    "This lighthouse was built by your grandfather.",
    "Your father maintained it.",
    "Now it's your turn.",
    "The beacon keeps the ships safe.",
    "You keep the beacon running.",
    "That is enough...",
]

# Player thoughts shown at the start of each night
SCRIPTS = {
    2:  ["Sun went down ten minutes early today.", "The shadows look... stretched."],
    4:  ["The light is casting a strange shadow on the water.", "It almost looks like rust.", "The daylight is barely lasting six hours now."],
    6:  ["Everything I touch is covered in this red dust.", "The sun didn't even rise until noon today.", "I can't see the dock without the lighthouse beam hitting it."],
}
FALLBACK_NIGHT_SCRIPT = ["The day lasted shorter yet again..."]

# Shown after each night
FINISH_SCRIPTS = {
    1:  ["The lens is clear.", "The light will carry further tonight."],
    2:  ["The pressure is logged.", "Numbers don't lie, even when they scare you."],
    3:  ["The cables hold.", "For now."],
    4:  ["The bulb is clean.", "The beam cuts through the dark like it should."],
    5:  ["The sensors are in place.", "The scientist seems satisfied."],
    6:  ["The shutters are locked.", "The red dust keeps falling."],
    7:  ["The doors are boarded.", "This is the last supply drop."],
    8:  ["The engine cools.", "The sound it made wasn't right."],
    9:  ["The light keeps spinning.", "Your arms are tired.", "It doesn't matter."],
    10: ["...", "The lighthouse shakes."],
}

# Shown after completing all day tasks
DAY_FINISH_SCRIPTS = {
    1:  ["The generator is running.", "Good enough for now."],
    2:  ["Pressure logged.", "The numbers are getting worse."],
    3:  ["Cables replaced.", "The light should hold another night."],
    4:  ["Bulb is clean.", "The beam is as strong as it can be."],
    5:  ["Sensors placed.", "The scientist seems to know something she isn't saying."],
    6:  ["Shutters locked.", "The red dust gets in everywhere."],
    7:  ["Doors boarded.", "Won't stop much, but it's something."],
    8:  ["Engine cooled down.", "It won't last much longer."],
    9:  ["Done.", "Hands are shaking."],
    10: [],
}

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
        "world_x": 650,
        "y": 360,
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
