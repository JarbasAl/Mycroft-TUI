from asciimatics.screen import Screen

"""
# Non exhaustive list
fonts = ["stampatello", "standard", "soft", "spliff", "smslant", "usa",
             "utopia", "varsity", "wavy", "weird", "3d_diagonal", "3x5",
             "5lineoblique", "64f1", "6x10", "6x9", "acrobatic", "big",
             "smscript", "stampate", "stacey", "stop", "straight", "sweet",
             "slscript", "small", "starwars", "univers"]
"""
TIME_FONT = "starwars"
DATE_FONT = "starwars"
TITLE_FONT = "small"

DEFAULT_COLOR = Screen.COLOUR_BLUE
TIME_COLOR = None
DATE_COLOR = None


def change_color(new_color):
    global DEFAULT_COLOR
    DEFAULT_COLOR = new_color


def get_color():
    return DEFAULT_COLOR


LOGS = [
    "/var/log/mycroft/skills.log",
    "/var/log/mycroft/audio.log",
    "/var/log/mycroft/voice.log",
    "/var/log/mycroft/enclosure.log"
]
