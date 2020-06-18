from asciimatics.widgets import Label
from jarbas_mycroft_gui.settings import TIME_COLOR, TIME_FONT, \
    DATE_COLOR, DATE_FONT, get_color, LOGS
from jarbas_mycroft_gui.render import pretty_dict, pretty_title
from jarbas_mycroft_gui.monitoring import start_log_monitor, filteredLog
import datetime


class BaseWidget(Label):
    def __init__(self, gui, screen):
        self.gui = gui
        self.screen = screen
        self._active_page = "None"
        self._active_skill = "None"
        self._vars = {}
        super().__init__(None)

    @property
    def active_skill(self):
        return self.gui.skill

    @property
    def active_page(self):
        return self.gui.page

    @property
    def page_data(self):
        return self.gui.vars

    def update(self, frame_no):
        raise NotImplementedError

    def render(self, buffer, color=None, x=None, y=None):
        # update
        x = x or self._x
        y = y or self._y
        (colour, attr, bg) = self._frame.palette[
            self._pick_palette_key("label", selected=False,
                                   allow_input_state=False)]
        if not color:
            color = get_color() or colour
        for i, text in enumerate(buffer):
            self._frame.canvas.paint(
                "{:{}{}}".format(text, self._align, self._w), x, y + i,
                color, attr, bg)


class VariablesWidget(BaseWidget):
    def update(self, frame_no):
        if self.active_skill in self.page_data:
            title = pretty_title("Variables")
            self.render(title.split("\n"))
            y_pad = len(title.split("\n")) + 1
            pretty = pretty_dict(
                self.page_data[self.active_skill],
                ignored_keys=["fill"])
            self.render(pretty.split("\n"), y=y_pad)


class TimeWidget(BaseWidget):
    def update(self, frame_no):
        try:
            time_str = self.page_data["mycroft-date-time.mycroftai"]["time_string"]
            date_str = self.page_data["mycroft-date-time.mycroftai"]["date_string"]
        except:
            time_str = ""
            date_str = ""
        if not date_str:
            date_str = str(datetime.datetime.today().date())
        # draw time string
        if time_str:
            time_str = pretty_title(time_str, font=TIME_FONT)

            hpad = (self.screen.width - len(time_str.split("\n")[0])) // 2
            vpad = (self.screen.height - len(time_str.split("\n")) -
                    len(date_str.split("\n"))) // 2
            self.render(time_str.split("\n"), TIME_COLOR, y=vpad, x=hpad)
        else:
            vpad = (self.screen.height - len(date_str.split("\n"))) // 2

        # draw date string
        date_str = pretty_title(date_str, font=DATE_FONT)
        hpad = (self.screen.width - len(date_str.split("\n")[0])) // 2
        vpad += len(date_str.split("\n")) + 1
        self.render(date_str.split("\n"), DATE_COLOR, y=vpad, x=hpad)


class HelpWidget(BaseWidget):
    def __init__(self, gui, screen):
        self.keys = {
            "H": "Help Screen",
            "P": "Picture Mode",
            "V": "Variables Mode",
            "C": "CommandLine chat",
            "M": "MessageBus monitor",
            "L": "Logs Viewer",
            "S": "Skills Viewer",
            "A": "AudioService Screen",
            "T": "Clock Screen",
            "R": "Change color to Red",
            "G": "Change color to Green",
            "B": "Change color to Blue",
            "J": "Credits",
            "X": "Exit"
        }
        super().__init__(gui, screen)

    def update(self, frame_no):
        title = pretty_title("Help")
        self.render(title.split("\n"))
        y_pad = len(title.split("\n")) + 1
        keys = pretty_dict(self.keys)
        self.render(keys.split("\n"), y=y_pad)


class LogsWidget(BaseWidget):
    def __init__(self, gui, screen):
        super().__init__(gui, screen)
        for log in LOGS:
            start_log_monitor(log)

    def update(self, frame_no):
        title = pretty_title("Logs")
        self.render(title.split("\n"))
        y_pad = len(title.split("\n")) + 1
        draw = []
        num = self.screen.height - y_pad
        logs = list(reversed(filteredLog))[:num]
        for l in reversed(logs):
            draw.append(l.strip())
        self.render(draw, y=y_pad)
