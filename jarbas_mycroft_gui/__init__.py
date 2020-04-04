from jarbas_mycroft_gui.mycroft_gui import DummyGUI
from pyfiglet import Figlet
from asciimatics.effects import Scroll, Mirage, Wipe, Cycle, Matrix, Print
from os.path import dirname, join, basename
from asciimatics.renderers import FigletText, SpeechBubble, ColourImageFile
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.screen import ManagedScreen
from asciimatics.exceptions import NextScene, StopApplication
from asciimatics.event import MouseEvent, KeyboardEvent
from asciimatics.widgets import Frame, TextBox, Layout, Label, Divider, Text, \
    PopUpDialog, Background, Widget
import logging

logging.getLogger("mycroft_bus_client.client.client").setLevel("ERROR")
logging.getLogger("asciimatics").setLevel("WARN")
from time import sleep
from pprint import pformat
from jarbas_utils import create_daemon


class MycroftGUI(DummyGUI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.screen = None

    def intro(self):

        scenes = []

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
                  self.screen.height - 9, x=(self.screen.width - width) // 2 + 1,
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
        scenes.append(Scene(effects, 100, name="Splash"))

        effects = [
            Matrix(self.screen, stop_frame=200),
            Mirage(
                self.screen,
                FigletText("Mycroft"),
                self.screen.height // 2 - 3,
                Screen.COLOUR_GREEN,
                start_frame=100,
                stop_frame=200),
            Wipe(self.screen, start_frame=150),
            Cycle(
                self.screen,
                FigletText("Mycroft GUI"),
                self.screen.height // 2 - 3,
                start_frame=200)
        ]
        scenes.append(Scene(effects, 250, name="Title"))
        return scenes

    def _refresh(self):
        while True:
            sleep(1)
            self.draw()

    def _run(self, screen):
        self.screen = screen
        scenes = self.intro()
        scenes += [Scene([DisplayFrame(self.screen, self)], -1)]
        scenes += self.credits()
        create_daemon(self._refresh)
        self.screen.play(scenes, repeat=False)

    def run(self):
        if not self.connected:
            self.connect()
        Screen.wrapper(s._run)

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
        scenes.append(Scene(effects, duration=50,
                            name="Exit", ))
        effects = [

            Scroll(self.screen, 3),
            Mirage(
                self.screen,
                FigletText("Written by:"),
                self.screen.height + 8,
                Screen.COLOUR_GREEN),
            Mirage(
                self.screen,
                FigletText("JarbasAi"),
                self.screen.height + 16,
                Screen.COLOUR_GREEN)
        ]

        scenes.append(Scene(effects, (self.screen.height + 24) * 3,
                            name="Credits"))
        return scenes


class DisplayWidget(Label):
    def __init__(self, gui):
        self.gui = gui
        super().__init__(None)

    def update(self, frame_no):
        (colour, attr, bg) = self._frame.palette[
            self._pick_palette_key("label", selected=False,
                                   allow_input_state=False)]
        for i, text in enumerate(self.gui.buffer):
            self._frame.canvas.paint(
                "{:{}{}}".format(text, self._align, self._w), self._x,
                self._y + i, colour, attr, bg)
        self._value = "\n".join(self.gui.buffer)


class DisplayFrame(Frame):
    def __init__(self, screen, gui):
        super(DisplayFrame, self).__init__(screen, screen.height, screen.width,
                                           has_shadow=False, has_border=False,
                                           name="GUI")
        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)
        d = DisplayWidget(gui)
        layout.add_widget(d)
        self.fix()
        self.set_theme("monochrome")

    def process_event(self, event):
        if isinstance(event, KeyboardEvent):
            if event.key_code == 120 or event.key_code == 88:  # press x
                raise NextScene("Exit")
            else:
                # Ignore any other key press.
                return event
        elif isinstance(event, MouseEvent):
            # Ignore other mouse events.
            return event
        else:
            # Ignore other events
            return event

        # If we got here, we processed the event - swallow it.
        return None


if __name__ == "__main__":
    s = MycroftGUI()
    s.run()
