from jarbas_mycroft_gui import DummyGUI
from pyfiglet import Figlet
from asciimatics.effects import Scroll, Mirage, Wipe, Cycle, Matrix, Print
from os.path import dirname, join, basename
from asciimatics.renderers import FigletText, SpeechBubble, ColourImageFile
from asciimatics.scene import Scene
from asciimatics.exceptions import ResizeScreenError
from asciimatics.screen import Screen
import logging
from jarbas_mycroft_gui.pages import VariablesScreen, TimeScreen, HelpScreen
from jarbas_mycroft_gui.settings import BASE_COLOR
import sys
from asciimatics.exceptions import NextScene
logging.getLogger("mycroft_bus_client.client.client").setLevel("ERROR")
logging.getLogger("asciimatics").setLevel("WARN")
from time import sleep
from pprint import pformat
from jarbas_utils import create_daemon
from jarbas_utils.log import LOG


class MycroftGUI(DummyGUI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.screen = None

    def pages(self):
        scenes = [Scene([TimeScreen(self.screen, self)], -1, name="Time")]
        scenes += [Scene([HelpScreen(self.screen, self)], -1, name="Help")]

        return scenes

    def intro(self):
        scenes = []
        effects = [
            Mirage(
                self.screen,
                FigletText("Mycroft GUI"),
                self.screen.height // 2 - 3,
                BASE_COLOR,
                start_frame=20,
                stop_frame=150)
        ]
        scenes.append(Scene(effects, 200, name="Splash"))

        text = Figlet(font="banner", width=200).renderText("JARBASAI")
        width = max([len(x) for x in text.split("\n")])

        effects = [
            Print(self.screen,
                  ColourImageFile(self.screen,
                                  join(dirname(__file__), "logo.gif"),
                                  self.screen.height - 5,
                                  uni=self.screen.unicode_aware,
                                  dither=self.screen.unicode_aware),
                  y=1),
            Print(self.screen,
                  FigletText("JARBASAI", "banner"),
                  self.screen.height - 9,
                  x=(self.screen.width - width) // 2 + 1,
                  colour=Screen.COLOUR_BLACK,
                  bg=Screen.COLOUR_BLACK,
                  speed=1),
            Print(self.screen,
                  FigletText("JARBASAI", "banner"),
                  self.screen.height - 9,
                  colour=Screen.COLOUR_WHITE,
                  bg=Screen.COLOUR_WHITE,
                  speed=1),
        ]
        scenes.append(Scene(effects, duration=30, name="Jarbas"))
        return scenes

    def _refresh(self):
        last_bug = None
        while True:
            sleep(0.2)
            if self.buffer != last_bug:
                last_bug = self.buffer
                self.draw()

    def on_message(self, message):
        msg_type = message.get("type")
        if msg_type == "mycroft.session.set":
            skill = message.get("namespace")
            if skill == "mycroft-date-time.mycroftai":
                raise NextScene("Time")
            else:
                raise NextScene("Variables")

    def _run(self, screen, start_scene=None):
        self.screen = screen
        intro = self.intro()
        scenes = self.pages()
        scenes += intro
        scenes += [Scene([VariablesScreen(self.screen, self)], -1,
                         name="Variables")]
        scenes += self.credits()
        create_daemon(self._refresh)
        self.screen.play(scenes,
                         repeat=False,
                         stop_on_resize=True,
                         start_scene=start_scene or intro[0])

    def run(self, start_scene=None):
        if not self.connected:
            self.connect()
        try:
            Screen.wrapper(self._run, arguments=[start_scene])
        except ResizeScreenError as e:
            self.run(e.scene)
        except Exception as e:
            LOG.exception(e)
            sys.exit(0)

    def _draw_buffer(self):
        # TODO use real widgets
        self.buffer = []
        if self.skill:
            self.buffer.append("Active Skill:" + self.skill)

            if self.page:
                self.buffer.append("Page:" + basename(self.page))
            else:
                self.buffer.append("Page: None")

            if self.skill in self.vars:
                for v in dict(self.vars[self.skill]):
                    if self.vars[self.skill][v]:
                        self.buffer.append("{}:".format(v))
                        pretty = pformat(self.vars[self.skill][v])
                        for l in pretty.split("\n"):
                            self.buffer.append("    " + l)

    def draw(self):
        self.screen.force_update()

    def credits(self):
        scenes = []
        effects = [Print(self.screen,
                         SpeechBubble("Exiting GUI"),
                         self.screen.height // 2 - 1,
                         attr=Screen.A_BOLD)]
        scenes.append(Scene(effects, duration=10,
                            name="Exit", ))

        return scenes


if __name__ == "__main__":
    s = MycroftGUI()
    s.run()
