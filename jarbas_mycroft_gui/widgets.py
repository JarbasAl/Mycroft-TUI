from asciimatics.widgets import Label
from jarbas_mycroft_gui.settings import TIME_COLOR, TIME_FONT, \
    DATE_COLOR, DATE_FONT, get_color, LOGS, DEBUG_COLOR, INFO_COLOR, \
    WARNING_COLOR, ERROR_COLOR, DEBUG
from jarbas_mycroft_gui.render import pretty_dict, pretty_title
from jarbas_mycroft_gui.monitoring import start_log_monitor, mergedLog
import datetime
import random
import time
from jarbas_mycroft_gui.bus import fake_bus, Message


class BaseWidget(Label):
    def __init__(self, gui, screen, name=None):
        self.title = name or self.__class__.__name__
        self.gui = gui
        self.screen = screen
        self._active_page = "None"
        self._active_skill = "None"
        self._vars = {}
        self.motd = []
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
    def __init__(self, gui, screen, title="Variables"):
        self.old_vars = {}
        self.pages = []
        super().__init__(gui, screen, title)

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
        self.motd = ["Active Skill: " + self.active_skill]
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
    def __init__(self, gui, screen, title="Help"):
        self.keys = {
            "H": "Help Screen",
            "P": "Picture Mode",
            "V": "Variables Mode",
            "C": "CommandLine chat",
            "M": "MessageBus monitor",
            "L": "Logs Viewer",
            "N": "Network Logs",
            "S": "Skills Viewer",
            "A": "AudioService Screen",
            "T": "Clock Screen",
            "R": "Change color to Red",
            "G": "Change color to Green",
            "B": "Change color to Blue",
            "J": "Credits",
            "X": "Exit"
        }
        super().__init__(gui, screen, title)
        self.motd = [
            "Found an issue?\nhttps://github.com/JarbasAl/Mycroft_cli_GUI",
            "Yes, this is beta and buggy"
        ]

    def update(self, frame_no):
        y_pad = self.render_title()
        keys = pretty_dict(self.keys)
        self.render(keys.split("\n"), y=y_pad)


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

    def get_logs(self, num=20):
        if len(self.buffer) > num:
            self.buffer = self.buffer[-1 * num:]
        return self.buffer

    def update(self, frame_no):
        y_pad = self.render_title()
        num = self.screen.height - y_pad
        for l in self.get_logs(num):
            clean = [l.strip()]
            self.render(clean, y=y_pad)
            y_pad += 1
