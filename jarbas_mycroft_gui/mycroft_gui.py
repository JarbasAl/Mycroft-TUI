from jarbas_mycroft_gui import DummyGUI
from pyfiglet import Figlet
from asciimatics.effects import Mirage, Print
from os.path import dirname, join
from asciimatics.renderers import FigletText, SpeechBubble, ColourImageFile
from asciimatics.scene import Scene
from asciimatics.exceptions import ResizeScreenError
from asciimatics.screen import Screen
import logging
from jarbas_mycroft_gui.pages import VariablesScreen, TimeScreen, \
    HelpScreen, LogsScreen, NetworkScreen, BusScreen
from jarbas_mycroft_gui.settings import DEFAULT_COLOR
import sys
logging.getLogger("mycroft_bus_client.client.client").setLevel("ERROR")
logging.getLogger("asciimatics").setLevel("WARN")
from jarbas_utils.log import LOG
from jarbas_utils import create_daemon
from time import sleep
from jarbas_mycroft_gui.bus import fake_bus, Message


class MycroftGUI(DummyGUI):
    def __init__(self, refresh_rate=1, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.screen = None

        self.needs_refresh = False
        self.refresh_rate = refresh_rate
        fake_bus.on("gui.cli.refresh_page", self.signaled_refresh)

    def refresh_loop(self):
        while True:
            sleep(self.refresh_rate)
            #self.needs_refresh = True
            if self.needs_refresh:
                self.screen.force_update()
                #self.screen.refresh()
                self.needs_refresh = False
            else:
                fake_bus.emit(Message("gui.cli.refresh_check"))

    def signaled_refresh(self, message=None):
        self.needs_refresh = True

    def pages(self):
        scenes = [Scene([TimeScreen(self.screen, self)], -1, name="Time")]
        scenes += [Scene([HelpScreen(self.screen, self)], -1, name="Help")]
        scenes += [Scene([LogsScreen(self.screen, self)], -1, name="Logs")]
        scenes += [Scene([NetworkScreen(self.screen, self)], -1,
                         name="Network")]
        scenes += [Scene([BusScreen(self.screen, self)], -1, name="Bus")]

        return scenes

    def intro(self):
        scenes = []
        effects = [
            Mirage(
                self.screen,
                FigletText("Mycroft GUI"),
                self.screen.height // 2 - 3,
                DEFAULT_COLOR,
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

    def _run(self, screen, start_scene=None):
        self.screen = screen
        create_daemon(self.refresh_loop)
        intro = self.intro()
        scenes = self.pages()
        scenes += intro
        scenes += [Scene([VariablesScreen(self.screen, self)], -1,
                         name="Variables")]
        scenes += self.credits()
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
