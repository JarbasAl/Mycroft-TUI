from pyfiglet import Figlet
from asciimatics.effects import Scroll, Mirage, Wipe, Cycle, Matrix, \
    BannerText, Stars, Print
from os.path import dirname, join
from asciimatics.renderers import FigletText, SpeechBubble, Rainbow, Fire, \
    ColourImageFile
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.exceptions import ResizeScreenError
import sys


def _credits(screen):
    scenes = []

    text = Figlet(font="banner", width=200).renderText("JARBASAI")
    width = max([len(x) for x in text.split("\n")])

    effects = [
        Print(screen,
              ColourImageFile(screen, join(dirname(__file__), "logo.gif"),
                              screen.height - 5,
                              uni=screen.unicode_aware,
                              dither=screen.unicode_aware),
              y=1),
        Print(screen,
              FigletText("JARBASAI", "banner"),
              screen.height - 9, x=(screen.width - width) // 2 + 1,
              colour=Screen.COLOUR_BLACK,
              bg=Screen.COLOUR_BLACK,
              speed=1),
        Print(screen,
              FigletText("JARBASAI", "banner"),
              screen.height - 9,
              colour=Screen.COLOUR_WHITE,
              bg=Screen.COLOUR_WHITE,
              speed=1),
    ]
    scenes.append(Scene(effects, 100))

    effects = [
        Matrix(screen, stop_frame=200),
        Mirage(
            screen,
            FigletText("Mycroft"),
            screen.height // 2 - 3,
            Screen.COLOUR_GREEN,
            start_frame=100,
            stop_frame=200),
        Wipe(screen, start_frame=150),
        Cycle(
            screen,
            FigletText("Mycroft GUI"),
            screen.height // 2 - 3,
            start_frame=200)
    ]
    scenes.append(Scene(effects, 250, clear=False))


    effects = [
        Print(screen,
              SpeechBubble("NOT IMPLEMENTED."), screen.height // 2 - 1,
              attr=Screen.A_BOLD)
    ]
    scenes.append(Scene(effects, -1))

    effects = [
        Scroll(screen, 3),
        Mirage(
            screen,
            FigletText("Written by:"),
            screen.height + 8,
            Screen.COLOUR_GREEN),
        Mirage(
            screen,
            FigletText("JarbasAi"),
            screen.height + 16,
            Screen.COLOUR_GREEN)
    ]
    scenes.append(Scene(effects, (screen.height + 24) * 3))

    effects = [
        Print(screen,
              SpeechBubble("Press 'X' to exit."), screen.height // 2 - 1, attr=Screen.A_BOLD)
    ]
    scenes.append(Scene(effects, -1))


    screen.play(scenes, stop_on_resize=True)



if __name__ == "__main__":
    while True:
        try:
            Screen.wrapper(_credits)
            sys.exit(0)
        except ResizeScreenError:
            pass

