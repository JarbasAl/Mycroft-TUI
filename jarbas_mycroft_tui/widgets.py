from asciimatics.widgets import Label, Text, Screen
from asciimatics.event import KeyboardEvent
from jarbas_mycroft_tui.settings import TIME_COLOR, TIME_FONT, \
    DATE_COLOR, DATE_FONT, get_color, LOGS, DEBUG_COLOR, INFO_COLOR, \
    WARNING_COLOR, ERROR_COLOR, DEBUG, INPUT_COLOR, OUTPUT_COLOR
from jarbas_mycroft_tui.render import pretty_dict, pretty_title
from jarbas_mycroft_tui.monitoring import start_log_monitor, mergedLog
import datetime
import random
import time
from jarbas_mycroft_tui.bus import fake_bus, Message
from jarbas_mycroft_tui.util import camel_case_split


class BaseWidget(Label):
    def __init__(self, gui, screen, name=None):
        self.title = name or self.__class__.__name__
        self.gui = gui
        self.screen = screen
        self._active_page = "None"
        self._active_skill = "None"
        self._vars = {}
        self.motd = []
        self.footer = ["press X to Exit, press H for Help"]
        self.needs_refresh = False
        super().__init__(None)
        fake_bus.on("gui.cli.refresh_check", self.check_if_refresh)

    def refresh(self):
        self.needs_refresh = False
        fake_bus.emit(Message("gui.cli.refresh_page",
                              {"widget": self.title}))

    def check_if_refresh(self, message=None):
        if self.needs_refresh:
            self.refresh()

    def render_title(self, render_motd=True):
        # only change motd on new minutes
        seed = str(datetime.datetime.now().hour) + \
               str(datetime.datetime.now().day) + \
               str(datetime.datetime.now().month) + \
               str(datetime.datetime.now().minute) + \
               str(datetime.datetime.now().year)
        random.seed(int(seed))

        title = pretty_title(self.title)
        self.render(title.split("\n"))
        y_pad = len(title.split("\n"))
        if len(self.motd) and render_motd:
            motd = random.choice(self.motd)
            self.render(motd.split("\n"), y=y_pad, x=5)
            y_pad += len(motd.split("\n")) + 1
        return y_pad

    def render_footer(self):
        # only change footer on new minutes
        seed = str(datetime.datetime.now().hour) + \
               str(datetime.datetime.now().day) + \
               str(datetime.datetime.now().month) + \
               str(datetime.datetime.now().minute) + \
               str(datetime.datetime.now().year)
        random.seed(int(seed))

        if len(self.footer):
            motd = random.choice(self.footer)
            self._frame.canvas.paint(motd,
                                     y=self.screen.height - len(
                                         motd.split("\n")),
                                     x=0)

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
        self.render_title()

    def render(self, buffer, color=None, x=None, y=None):
        # update
        x = x or self._x
        y = y or self._y
        if y == self.screen.height - 1:
            return  # reserved for footer
        (colour, attr, bg) = self._frame.palette[
            self._pick_palette_key("label", selected=False,
                                   allow_input_state=False)]
        if color is None:
            color = get_color() or colour
        for i, text in enumerate(buffer):
            self._frame.canvas.paint(
                "{:{}{}}".format(text, self._align, self._w), x, y + i,
                color, attr, bg)
            if y + i == self.screen.height - 1:
                break  # reserved for footer


class VariablesWidget(BaseWidget):
    def __init__(self, gui, screen, title="Variables"):
        super().__init__(gui, screen, title)
        self.old_vars = {}
        self.pages = []

    def check_if_refresh(self, message=None):
        if self.active_skill not in self.page_data:
            return
        needed = self.page_data != self.old_vars
        if needed:
            self.refresh()
            self.old_vars = self.page_data.copy()

    def update_pages(self):
        self.pages = []
        for skill in self.page_data:
            data = self.page_data[skill]
            for k in dict(data):
                if not data[k]:
                    data.pop(k)
            pretty = pretty_dict(data, ignored_keys=["fill",
                                                     "viseme"])
            self.pages.append(pretty)

    def update(self, frame_no):
        self.motd = ["Active Skill: " + str(self.active_skill)]
        y_pad = self.render_title()
        if self.active_skill in self.page_data:
            data = self.page_data[self.active_skill]
            for k in dict(data):
                if not data[k]:
                    data.pop(k)
            pretty = pretty_dict(data, ignored_keys=["fill",
                                                     "viseme"])
            self.pages.insert(0, pretty)
            self.render(pretty.split("\n"), y=y_pad)
            self.render_footer()


class TimeWidget(BaseWidget):
    def __init__(self, gui, screen, title="Time"):
        super().__init__(gui, screen, title)
        self.last_check = time.time()

    def check_if_refresh(self, message=None):
        needed = False
        if time.time() - self.last_check > 60:
            # once per minute
            needed = True
            self.last_check = time.time()
        if needed:
            self.refresh()

    def update(self, frame_no):
        try:
            time_str = self.page_data["mycroft-date-time.mycroftai"][
                "time_string"]
            date_str = self.page_data["mycroft-date-time.mycroftai"][
                "date_string"]
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
    def __init__(self, gui, screen, title="Help"):
        super().__init__(gui, screen, title)
        self.rows = [
            {"U": "Utterances",
             "M": "MessageBus monitor",
             "L": "Logs Viewer",
             "V": "GUI Variables",
             "N": "Network Logs",
             "R": "Change color to Red",
             "G": "Change color to Green",
             "B": "Change color to Blue",
             "T": "Clock Screen",
             "H": "Help Screen",
             "X": "Exit"}
        ]

        self.motd = [
            "Found an issue?\nhttps://github.com/JarbasAl/Mycroft_cli_GUI",
            "Yes, this is beta and buggy"
        ]

    def update(self, frame_no):
        y_pad = self.render_title()
        for row in self.rows:
            keys = pretty_dict(row)
            self.render(keys.split("\n"), y=y_pad)
            y_pad += len(keys.split("\n"))


class LogsWidget(BaseWidget):
    _log_buffer = []

    def __init__(self, gui, screen, title="Logs"):
        super().__init__(gui, screen, title)
        for log in LOGS:
            start_log_monitor(log)
        self.blacklist = True
        self.log_filters = [
            "mouth.viseme",
            "mouth.display",
            "mouth.icon",
            "Mark2",
            "mycroft.identity",
            "mycroft.api:refresh_token",
            "mycroft.client.enclosure",
            "werkzeug",  # personal backend / Hivemind
            "tornado.access",  # bus
            "mycroft.skills.skill_manager:_get_skill_directories",
            "No skill settings changes since last download",
            "DEBUG | print"
        ]
        self.motd = [
            "If you are connecting to a remote mycroft logs will be empty",
            "You can change the logs path in ~/.mycroft/simple_gui.conf",
            "You can usually find the logs at /var/log/mycroft",
            "Logs are extracted from /var/log/mycroft/xxx.log",
            "No logs?\nMake sure logs are enabled, only new logs will be "
            "displayed"
        ]

    def check_if_refresh(self, message=None):
        needed = False
        num = len(self._log_buffer)
        logs = self.get_logs(num)
        if logs != self._log_buffer:
            needed = True

        if needed:
            self.refresh()

    def get_logs(self, num=20):
        logs = list(reversed(mergedLog))
        for idx, line in enumerate(logs):
            if self.blacklist:
                for f in self.log_filters:
                    if f in line:
                        logs[idx] = ""
            else:
                whitelisted = False
                for f in self.log_filters:
                    if f in line:
                        whitelisted = True
                if not whitelisted:
                    logs[idx] = ""
        logs = [l for l in logs if l.strip()]
        logs = logs[:num]
        return list(reversed(logs))

    def update(self, frame_no):
        y_pad = self.render_title()
        num = self.screen.height - y_pad
        LogsWidget._log_buffer = self.get_logs(num)
        for l in self._log_buffer:
            clean = [l.strip()]
            color = INFO_COLOR
            if "DEBUG |" in l:
                color = DEBUG_COLOR
                if not DEBUG:
                    continue
            if "ERROR |" in l or "EXCEPTION |" in l:
                color = ERROR_COLOR
            if "WARN |" in l or "WARNING |" in l:
                color = WARNING_COLOR
            self.render(clean, y=y_pad, color=color)
            y_pad += 1
        self.render_footer()


class NetworkWidget(LogsWidget):
    def __init__(self, gui, screen):
        super().__init__(gui, screen, "Network")
        self.blacklist = False
        self.log_filters = [
            "werkzeug",  # personal backend / Hivemind
            "tornado.access",  # bus
            "jarbas_hive_mind",
            " * Serving Flask app",
            "urllib",
            "requests",
            "mock_mycroft_backend"
        ]
        self.motd = [
            "Ditch the backend\nInstall "
            "https://github.com/JarbasSkills/skill-mock-backend",
            "Enforce your privacy\nGithub: "
            "https://github.com/OpenJarbas/mock-backend",
            "Join the HiveMind, Enable mesh networking\nGithub: "
            "https://github.com/OpenJarbas/HiveMind-core",
            "Let your devices talk to each other\nInstall "
            "https://github.com/JarbasSkills/skill-hivemind",
            "Deploy voice satellites\nGithub: "
            "https://github.com/OpenJarbas/HiveMind-voice-sat",
            "NOTE: this is monitoring incoming requests only",
            "NOTE: outgoing requests might not be logged",
            "These logs should help you debug the mock-backend and HiveMind "
            "skills",
            "CAUTION: The Mycroft bus is an open websocket with no built-in "
            "security measures.\nYou are responsible for protecting the "
            "local port 8181 with a firewall as appropriate.",
            "Do not expose the messagebus, for that you have the HiveMind\n"
            "Github: https://github.com/OpenJarbas/HiveMind-core",
            "Quick tip: ufw deny 8181",
            "Is your messagebus exposed?\nTake a look at what you might be "
            "leaking in the Bus Monitor page (press M)"
        ]


class BusWidget(BaseWidget):
    def __init__(self, gui, screen, title="Bus Monitor"):
        super().__init__(gui, screen, title)
        self.msg_filters = []
        self.motd = [
            "Live messagebus feed",
            "If you are connecting from an external host, STOP!"
            "\nThe messagebus should be firewalled",
            "Protect your messagebus\nhttps://github.com/Nhoya/MycroftAI-RCE",
            "Do not expose the messagebus, for that you have the HiveMind\n"
            "Github: https://github.com/OpenJarbas/HiveMind-core",
            "CAUTION: The Mycroft bus is an open websocket with no built-in "
            "security measures.\nYou are responsible for protecting the "
            "local port 8181 with a firewall as appropriate."
        ]
        self.buffer = []
        self.gui.bus.on("message", self.handle_message)

    def handle_message(self, message):
        message = str(message)
        if message in self.buffer:
            self.buffer.remove(message)
        self.buffer.append(message)
        self.needs_refresh = True

    def get_messages(self, num=20):
        if len(self.buffer) > num:
            self.buffer = self.buffer[-1 * num:]
        return self.buffer

    def update(self, frame_no):
        y_pad = self.render_title()
        num = self.screen.height - y_pad
        for l in self.get_messages(num):
            clean = [l.strip()]
            self.render(clean, y=y_pad)
            y_pad += 1
        self.render_footer()


class UtterancesWidget(BaseWidget):
    def __init__(self, gui, screen, title="Utterances"):
        super().__init__(gui, screen, title)
        self.msg_filters = []
        self.motd = [
            "Chat with mycroft"
        ]
        self.buffer = []
        self.gui.bus.on("speak", self.handle_speak)
        self.gui.bus.on("recognizer_loop:utterance", self.handle_utterance)

    def handle_utterance(self, message):
        platform = message.context.get("platform") or \
                   message.context.get("client_name")
        source = message.context.get("source") or "Broadcast"
        words = camel_case_split(source).split(" ")
        source = " ".join(w.capitalize() for w in words)
        if platform:
            words = camel_case_split(platform).split(" ")
            platform = " ".join(w.capitalize() for w in words)
            source += " ({sauce})".format(sauce=platform)
        message = source + ": " + message.data["utterances"][0]
        message = "INPUT |" + message
        self.buffer.append(message)
        self.needs_refresh = True

    def handle_speak(self, message):
        source = message.context.get("destination") or "Broadcast"
        words = camel_case_split(source).split(" ")
        source = " ".join(w.capitalize() for w in words)
        source = "Mycroft ({sauce}): ".format(sauce=source)
        message = source + message.data["utterance"]
        message = "OUTPUT |" + message
        self.buffer.append(message)
        self.needs_refresh = True

    def utterances(self, num=20):
        if len(self.buffer) > num:
            self.buffer = self.buffer[-1 * num:]
        return self.buffer

    def update(self, frame_no):
        y_pad = self.render_title()
        num = self.screen.height - y_pad
        for l in self.utterances(num):
            color = None
            if "INPUT |" in l:
                color = INPUT_COLOR
            elif "OUTPUT |" in l:
                color = OUTPUT_COLOR
            clean = [l.replace("OUTPUT |", "").replace("INPUT |", "").strip()]
            self.render(clean, y=y_pad, color=color)
            y_pad += 1
            if y_pad == self.screen.height - 2:
                break
        self.render_footer()


class UtteranceInput(Text):
    def __init__(self, gui, screen, title="Input"):
        self.title = title
        self.gui = gui
        self.screen = screen
        self.input_enabled = False
        super().__init__(on_change=self.update)

    def update(self, frame_no=0):
        # enforce bottom of screen
        self._y = self.screen.height - 2
        color = get_color()
        self._frame.canvas.paint("Input: " + self.value, x=0, y=self._y,
                                 colour=color)
        if self.input_enabled:
            self._frame.canvas.paint("Press Ctrl+X to disable input", x=0,
                                     y=self.screen.height - 1)
        else:
            self._frame.canvas.paint("Press Ctrl+I to enable input", x=0,
                                     y=self.screen.height - 1)

    def handle_input(self):
        utterance = self.value
        if utterance:
            self.gui.bus.emit(
                Message("recognizer_loop:utterance",
                        {"utterances": [utterance]},
                        {"source": "Admin Panel",
                         "destination": "skills"}))
        self.value = ""

    def process_event(self, event):
        if isinstance(event, KeyboardEvent):
            if not self.input_enabled and \
                    (event.key_code == Screen.ctrl("i") or
                     event.key_code == -301):
                self.input_enabled = True
                # self.update(0)
            elif self.input_enabled and event.key_code == Screen.ctrl("x"):
                self.input_enabled = False
                # self.update(0)
            elif not self.input_enabled:
                return event
            elif event.key_code == 10:
                self.handle_input()
            elif event.key_code == Screen.KEY_BACK:
                if self._column > 0:
                    # Delete character in front of cursor.
                    self._set_and_check_value(
                        "".join([self._value[:self._column - 1],
                                 self._value[self._column:]]))
                    self._column -= 1
            elif event.key_code == Screen.KEY_DELETE:
                if self._column < len(self._value):
                    self._set_and_check_value(
                        "".join([self._value[:self._column],
                                 self._value[self._column + 1:]]))
            elif event.key_code == Screen.KEY_LEFT:
                self._column -= 1
                self._column = max(self._column, 0)
            elif event.key_code == Screen.KEY_RIGHT:
                self._column += 1
                self._column = min(len(self._value), self._column)
            elif event.key_code == Screen.KEY_HOME:
                self._column = 0
            elif event.key_code == Screen.KEY_END:
                self._column = len(self._value)
            elif event.key_code >= 32:
                # Enforce required max length - swallow event if not allowed
                if self._max_length is None or len(
                        self._value) < self._max_length:
                    # Insert any visible text at the current cursor position.
                    self._set_and_check_value(chr(event.key_code)
                        .join(
                        [self._value[:self._column],
                         self._value[self._column:]]))
                    self._column += 1
            else:
                # Ignore any other key press.
                return event
        else:
            # Ignore other events
            return event

        # If we got here, we processed the event - swallow it
        return None


class WIPWidget(BaseWidget):
    def __init__(self, gui, screen, title="Not Implemented"):
        super().__init__(gui, screen, title)
        self.motd = [
            "Contribute: \nhttps://github.com/JarbasAl/Mycroft_cli_GUI"
        ]
