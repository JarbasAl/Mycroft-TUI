from asciimatics.exceptions import NextScene
from asciimatics.event import MouseEvent, KeyboardEvent
from asciimatics.widgets import Frame, Layout, Label
from art import text2art
from jarbas_mycroft_gui.settings import TIME_COLOR, TIME_FONT, \
    DATE_COLOR, DATE_FONT, BASE_COLOR
from pprint import pformat
from jarbas_mycroft_gui.util import split_sentences
from rich.console import Console
from rich.table import Table


class RichDraw(Console):
    def __init__(self):
        super().__init__(record=True)

    def _check_buffer(self) -> None:
        """Check if the buffer may be rendered."""
        if self._buffer_index == 0:
            text = self._render_buffer()


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
        return self.gui.skill

    @property
    def active_page(self):
        return self.gui.page

    @property
    def page_data(self):
        return self.gui.vars

    def handle_wikipedia(self):
        summary = self.page_data[self.active_skill].get("summary")
        if summary:
            canvas = RichDraw()
            table = Table(expand=True)
            table.add_column("summary", justify="center")
            for sentence in split_sentences(summary):
                table.add_row(sentence)
            canvas.print(table)
            self._value = canvas.export_text()
            self.render(self._value.split("\n"))
            return True
        return False

    def handle_time(self):
        time_str = self.page_data[self.active_skill]["time_string"]
        date_str = self.page_data[self.active_skill]["date_string"]
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

    def handle_page(self):
        handled = False
        if self.active_skill in self.page_data:
            if self.active_skill == "mycroft-date-time.mycroftai":
                handled = self.handle_time()
            elif self.active_skill == "mycroft-wiki.mycroftai":
                handled = self.handle_wikipedia()

            # default handler, just print buffer
            if not handled:

                def print_dict(data, expand=True):
                    s = ""

                    canvas = RichDraw()
                    vals = []
                    val_len = 0
                    var_len = 0
                    table = Table(expand=expand)
                    # first pass, standalone values
                    for var in data:
                        if not isinstance(data[var], dict) and \
                                not isinstance(data[var], list):
                            val = str(data[var])
                            var_len += len(var)
                            if not val:
                                continue
                            if len(val) + val_len >= self.screen.width // 2 or\
                                    var_len >= self.screen.width // 2:
                                table.add_row(*vals)
                                canvas.print(table)
                                # new table
                                vals = []
                                val_len = 0
                                var_len = 0
                                table = Table(expand=expand)
                            else:
                                table.add_column(var, justify="center")
                                vals.append(val)
                                val_len += len(val)

                    if len(vals):
                        table.add_row(*vals)
                        canvas.print(table)
                    # second pass, dicts
                    for var in data:
                        if isinstance(data[var], dict):
                            s += print_dict(data[var], expand=expand)
                    # third pass, lists
                    for var in data:
                        if isinstance(data[var], list):
                            for val in data[var]:
                                if isinstance(val, dict):
                                    s += print_dict(val, expand=expand)
                                else:
                                    table = Table(expand=expand)
                                    table.add_column(var)
                                    table.add_row(pformat(val))
                                    canvas.print(table)

                    s = canvas.export_text() + s
                    return s

                try:
                    self._value = print_dict(self.page_data[self.active_skill])
                except:
                    self._value = print_dict(self.page_data[self.active_skill],
                                             expand=False)
                self.render(self._value.split("\n"))
                handled = True
        return handled

    def render(self, buffer, color=None, x=None, y=None):
        # update
        x = x or self._x
        y = y or self._y
        (colour, attr, bg) = self._frame.palette[
            self._pick_palette_key("label", selected=False,
                                   allow_input_state=False)]
        if not color:
            color = BASE_COLOR or colour
        for i, text in enumerate(buffer):
            self._frame.canvas.paint(
                "{:{}{}}".format(text, self._align, self._w), x, y + i,
                color, attr, bg)

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
