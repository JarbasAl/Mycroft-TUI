from jarbas_mycroft_gui.gui import DummyGUI
import curses
from os.path import basename
from pprint import pformat
from time import sleep


class CursesGUI(DummyGUI):
    def __init__(self, host="0.0.0.0", port=8181, name=None, debug=0,
                 refresh_rate=0.5):
        super().__init__(host, port, name, debug)
        self._debug_msg = []
        self._init_curses()
        self.refresh_rate = refresh_rate

    def _init_curses(self):
        # init curses
        self.window = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.window.keypad(1)
        curses.curs_set(0)

    def run(self):
        self.window.clrtobot()
        self.window.refresh()
        # process GUI input
        if not self.connected:
            self.connect()
        while True:
            sleep(self.refresh_rate)
            self.draw()

    def _draw_buffer(self):
        # TODO add some colors
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
        try:
            debug = "\n".join(self._debug_msg) + "\n" + 80 * "#"
            message = "\n".join(self.buffer)
            if self.debug > 0:
                message = debug + "\n" + message
            self.window.addstr(0, 0, message)
        except:
            pass
        self.window.clrtobot()
        self.window.refresh()


if __name__ == "__main__":
    gui = CursesGUI(debug=0)
    gui.run()
