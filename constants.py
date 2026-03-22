DAY_LENGTH = 10.0  # seconds

# changes color bw day and night. can maybe add an gradient change so i made it a dict for now
SKY_COLORS = {
    "day": (62, 75, 110),
    "night": (25, 20, 45),
}

SPEED = 200


#   {"x": <x_pos>, "y": <y_pos>, "label": <text_label for when close>},
INTERACTABLES = [
]

#   [<dialog1>, <dialog2>.... <dialogn>] must be string
# This is for interactibles. When we get close to interactibles, we can press E or X or something to interact with them
RESPONSES = [
]

GROUND_Y = 400

# index: list of dialogues
# index represents night number
SCRIPTS = {
    1: ["The beacon stutters.", "The rhythm is wrong."],
}
