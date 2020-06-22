from asciimatics.exceptions import NextScene
from asciimatics.event import MouseEvent, KeyboardEvent
from asciimatics.widgets import Frame, Layout
from asciimatics.screen import Screen
from jarbas_mycroft_tui.widgets import HelpWidget, VariablesWidget, \
    TimeWidget, LogsWidget, NetworkWidget, BusWidget, UtterancesWidget, \
    UtteranceInput, WIPWidget
from jarbas_mycroft_tui.settings import change_color


class BaseScreen(Frame):
    def __init__(self, screen, gui, has_shadow=False, has_border=False,
                 name="GUI", input=None, **kwargs):
        super().__init__(screen, screen.height, screen.width,
                         has_shadow=has_shadow, has_border=has_border,
                         name=name, **kwargs)
        self.gui = gui
        self.input = input
        self.set_theme("monochrome")

    def process_event(self, event):
        if self.input is not None:
            if self.input.process_event(event) is None:
                # handled by input widget
                return None
        if isinstance(event, KeyboardEvent):
            if event.key_code == 120 or event.key_code == 88:
                # press x
                raise NextScene("Exit")
            elif event.key_code == ord('h') or event.key_code == ord('H'):
                # press l
                raise NextScene("Help")
            elif event.key_code == ord('l') or event.key_code == ord('L'):
                # press l
                raise NextScene("Logs")
            elif event.key_code == ord('a') or event.key_code == ord('A'):
                # press a
                raise NextScene("WIP")
                raise NextScene("AudioService")
            elif event.key_code == ord('t') or event.key_code == ord('T'):
                # press t
                raise NextScene("Time")
            elif event.key_code == ord('p') or event.key_code == ord('P'):
                # press p
                raise NextScene("WIP")
                raise NextScene("Picture")
            elif event.key_code == ord('v') or event.key_code == ord('V'):
                # press v
                raise NextScene("Variables")
            elif event.key_code == ord('s') or event.key_code == ord('S'):
                # press s
                raise NextScene("WIP")
                raise NextScene("Skills")
            elif event.key_code == ord('j') or event.key_code == ord('J'):
                # press j
                raise NextScene("Jarbas")
            elif event.key_code == ord('u') or event.key_code == ord('U'):
                # press c
                raise NextScene("Chat")
            elif event.key_code == ord('m') or event.key_code == ord('M'):
                # press m
                raise NextScene("Bus")
            elif event.key_code == ord('n') or event.key_code == ord('N'):
                # press n
                raise NextScene("Network")
            elif event.key_code == ord('r') or event.key_code == ord('R'):
                # press r
                change_color(Screen.COLOUR_RED)
            elif event.key_code == ord('g') or event.key_code == ord('G'):
                # press g
                change_color(Screen.COLOUR_GREEN)
            elif event.key_code == ord('b') or event.key_code == ord('B'):
                # press b
                change_color(Screen.COLOUR_BLUE)
            else:
                # Ignore any other key press.
                return event
        elif isinstance(event, MouseEvent):
            # Ignore mouse events.
            return event
        else:
            # Ignore other events
            return event

        # If we got here, we processed the event - swallow it.
        return None


class HelpScreen(BaseScreen):
    def __init__(self, screen, gui, has_shadow=False, has_border=False,
                 name="Help"):
        super().__init__(screen, gui, has_shadow=has_shadow,
                         has_border=has_border, name=name)
        layout = Layout([40], fill_frame=False)
        self.add_layout(layout)
        d = HelpWidget(gui, screen)
        layout.add_widget(d)


class NetworkScreen(BaseScreen):
    def __init__(self, screen, gui, has_shadow=False, has_border=False,
                 name="Network"):
        super().__init__(screen, gui, has_shadow=has_shadow,
                         has_border=has_border, name=name)
        layout = Layout([screen.width - 2], fill_frame=False)
        self.add_layout(layout)
        d = NetworkWidget(gui, screen)
        layout.add_widget(d)


class LogsScreen(BaseScreen):
    def __init__(self, screen, gui, has_shadow=False, has_border=False,
                 name="Logs"):
        super().__init__(screen, gui, has_shadow=has_shadow,
                         has_border=has_border, name=name)
        layout = Layout([screen.width - 2], fill_frame=False)
        self.add_layout(layout)
        d = LogsWidget(gui, screen)
        layout.add_widget(d)


class TimeScreen(BaseScreen):
    def __init__(self, screen, gui, has_shadow=False, has_border=False,
                 name="Time"):
        super().__init__(screen, gui, has_shadow=has_shadow,
                         has_border=has_border, name=name)
        layout = Layout([screen.width - 2], fill_frame=False)
        self.add_layout(layout)
        d = TimeWidget(gui, screen)
        layout.add_widget(d)


class VariablesScreen(BaseScreen):
    def __init__(self, screen, gui, has_shadow=False, has_border=False,
                 name="Variables"):
        super().__init__(screen, gui, has_shadow=has_shadow,
                         has_border=has_border, name=name)
        layout = Layout([screen.width - 2], fill_frame=False)
        self.add_layout(layout)
        d = VariablesWidget(gui, screen)
        layout.add_widget(d)


class BusScreen(BaseScreen):
    def __init__(self, screen, gui, has_shadow=False, has_border=False,
                 name="Bus"):
        super().__init__(screen, gui, has_shadow=has_shadow,
                         has_border=has_border, name=name)
        layout = Layout([screen.width - 2], fill_frame=False)
        self.add_layout(layout)
        d = BusWidget(gui, screen)
        layout.add_widget(d)


class ChatScreen(BaseScreen):
    def __init__(self, screen, gui, has_shadow=False, has_border=False,
                 name="Utterances"):
        super().__init__(screen, gui, has_shadow=has_shadow,
                         has_border=has_border, name=name, is_modal=True)
        layout = Layout([screen.width - 2], fill_frame=False)
        self.add_layout(layout)
        d = UtterancesWidget(gui, screen)
        layout.add_widget(d)
        layout2 = Layout([screen.width - 2], fill_frame=False)
        self.add_layout(layout2)
        self.input = UtteranceInput(gui, screen)
        layout2.add_widget(self.input)


class WIPScreen(BaseScreen):
    def __init__(self, screen, gui, has_shadow=False, has_border=False,
                 name="WIP"):
        super().__init__(screen, gui, has_shadow=has_shadow,
                         has_border=has_border, name=name, is_modal=True)
        layout = Layout([screen.width - 2], fill_frame=False)
        self.add_layout(layout)
        d = WIPWidget(gui, screen)
        layout.add_widget(d)