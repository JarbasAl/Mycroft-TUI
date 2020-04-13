from asciimatics.exceptions import NextScene
from asciimatics.event import MouseEvent, KeyboardEvent
from asciimatics.widgets import Frame, Layout, Label
from art import text2art
from jarbas_mycroft_gui.settings import TIME_COLOR, TIME_FONT, DATE_COLOR, DATE_FONT


class DisplayWidget(Label):
    def __init__(self, gui, screen):
        self.gui = gui
        self.screen = screen
        self._active_page = "None"
        self._active_skill = "None"
        self._vars = {}
        super().__init__(None)

    @property
    def active_skill(self):
        if len(self.gui.buffer) > 1 and ":" in self.gui.buffer[0]:
            self._active_skill = self.gui.buffer[0].split(":")[1]
        return self._active_skill

    @property
    def active_page(self):
        if len(self.gui.buffer) > 1 and ":" in self.gui.buffer[1]:
            self._active_page = self.gui.buffer[1].split(":")[1]
        return self._active_page

    @property
    def page_data(self):
        if len(self.gui.buffer) > 1 and ":" in self.gui.buffer[0]:
            current_var = None
            for line in self.gui.buffer[1:]:
                line = line.strip()
                if line.endswith(":"):
                    current_var = line.rstrip(":")
                else:
                    current_val = line.rstrip("'\"").lstrip("'\"")
                    if current_var:
                        self._vars[current_var] = current_val
        return self._vars

    def handle_wikipedia(self):
        return False

    def handle_time(self):
        time_str = self.page_data.get("time_string")
        date_str = self.page_data.get("date_string")
        if not time_str or not date_str:
            return False
        # draw time string
        time_str = text2art(time_str, font=TIME_FONT)
        date_str = text2art(date_str, font=DATE_FONT)
        hpad = (self.screen.width - len(time_str.split("\n")[0])) // 2
        vpad = (self.screen.height - len(time_str.split("\n")) -
                len(date_str.split("\n"))) // 2

        draw = [line.replace("\r", "") for line in time_str.split("\n")]
        self.render(draw, TIME_COLOR, y=vpad, x=hpad)
        self._value = "\n".join(draw)

        # draw date string
        hpad = (self.screen.width - len(date_str.split("\n")[0])) // 2
        vpad += len(date_str.split("\n")) + 1
        draw = [line.replace("\r", "") for line in date_str.split("\n")]
        self.render(draw, DATE_COLOR, y=vpad, x=hpad)
        self._value += "\n".join(draw)
        return True

    def handle_weather(self):
        return False

    def handle_page(self):
        handled = False
        if self.active_skill == "mycroft-date-time.mycroftai":
            handled = self.handle_time()
        elif self.active_skill == "mycroft-wiki.mycroftai":
            handled = self.handle_wikipedia()
        elif self.active_skill == "mycroft-weather.mycroftai":
            handled = self.handle_weather()

        # default handler, just print buffer
        if not handled:
            handled = True
            self.render(self.gui.buffer)
            self._value = "\n".join(self.gui.buffer)
        return handled

    def render(self, buffer, color=None, x=None, y=None):
        # update
        x = x or self._x
        y = y or self._y
        (colour, attr, bg) = self._frame.palette[
            self._pick_palette_key("label", selected=False,
                                   allow_input_state=False)]
        colour = color or colour
        for i, text in enumerate(buffer):
            self._frame.canvas.paint(
                "{:{}{}}".format(text, self._align, self._w), x, y + i,
                colour, attr, bg)

    def update(self, frame_no):
        self.handle_page()


class DisplayFrame(Frame):
    def __init__(self, screen, gui):
        super(DisplayFrame, self).__init__(screen, screen.height, screen.width,
                                           has_shadow=False, has_border=False,
                                           name="GUI")
        layout = Layout([100], fill_frame=False)
        self.add_layout(layout)
        d = DisplayWidget(gui, screen)
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
