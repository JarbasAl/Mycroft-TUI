from os import getpid
from os.path import basename
import json
from time import sleep
from pprint import pformat

from jarbas_utils.log import LOG
from jarbas_utils.messagebus import get_mycroft_bus, MessageBusClient,\
    Message


def get_websocket(host, port, route='/', ssl=False, threaded=False):
    """
    Returns a connection to a websocket
    """
    client = MessageBusClient(host, port, route, ssl)
    if threaded:
        client.run_in_thread()
    return client


# helper to print in color
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class DummyGUI:
    def __init__(self, host="0.0.0.0", port=8181, name=None, debug=False):
        self.bus = get_mycroft_bus(host, port)
        self.loaded = []
        self.skill = None
        self.page = None
        self.vars = {}
        self.mycroft_ip = host
        self.gui_ws = None
        self.name = name or self.__class__.__name__.lower()
        self.debug = debug
        self.connected = False
        self.buffer = []

    def run(self):
        last_buffer = []
        if not self.connected:
            self.connect()
        while True:
            sleep(1)
            if self.buffer != last_buffer:
                self.draw()
                last_buffer = self.buffer

    @property
    def gui_id(self):
        return self.name + "_" + str(getpid())

    def connect(self):
        LOG.debug("Announcing GUI")
        self.bus.on('mycroft.gui.port', self._connect_to_gui)
        self.bus.emit(Message("mycroft.gui.connected",
                              {"gui_id": self.gui_id}))
        self.connected = True

    def _connect_to_gui(self, msg):
        # Attempt to connect to the port
        gui_id = msg.data.get("gui_id")
        if not gui_id == self.gui_id:
            # Not us, ignore!
            return

        # Create the websocket for GUI communications
        port = msg.data.get("port")
        if port:
            LOG.info("Connecting GUI on " + str(port))
            self.gui_ws = get_websocket(host=self.mycroft_ip,
                                        port=port, route="/gui")
            self.gui_ws.on("open", self.on_open)
            self.gui_ws.on("message", self.on_gui_message)
            self.gui_ws.run_in_thread()

    def on_open(self, message):
        LOG.debug("Gui connection open")

    def on_new_gui_data(self, data):
        pass

    def on_gui_message(self, payload):
        try:
            msg = json.loads(payload)
            if self.debug:
                LOG.debug("Msg: " + str(payload))
            msg_type = msg.get("type")
            if msg_type == "mycroft.session.set":
                skill = msg.get("namespace")
                self.skill = self.skill or skill
                data = msg.get("data")
                if skill not in self.vars:
                    self.vars[skill] = {}
                for d in data:
                    self.vars[skill][d] = data[d]
                self.on_new_gui_data(data)
            elif msg_type == "mycroft.session.list.insert":
                # Insert new namespace
                self.skill = msg['data'][0]['skill_id']
                self.loaded.insert(0, [self.skill, []])
            elif msg_type == "mycroft.gui.list.insert":
                # Insert a page in an existing namespace
                self.page = msg['data'][0]['url']
                pos = msg.get('position')
                # TODO sometimes throws IndexError: list index out of range
                # not invalid json, seems like either pos is out of range or
                # "mycroft.session.list.insert" message was missed
                # NOTE: only happened once with wiki skill, cant replicate
                self.loaded[0][1].insert(pos, self.page)
                #self.skill = self.loaded[0][0]
            elif msg_type == "mycroft.session.list.move":
                # Move the namespace at "pos" to the top of the stack
                pos = msg.get('from')
                self.loaded.insert(0, self.loaded.pop(pos))
            elif msg_type == "mycroft.session.list.remove":
                pos = msg.get('position')
                skill = msg.get("namespace")
                if self.skill == skill:
                    self.skill = None
                self.loaded.pop(pos)
            elif msg_type == "mycroft.events.triggered":
                # Switch selected page of namespace
                skill = msg['namespace']
                self.skill = self.skill or skill
                pos = msg['data']['number']
                for n in self.loaded:
                    if n[0] == skill:
                        # TODO sometimes pos throws
                        #  IndexError: list index out of range
                        # ocasionally happens with weather skill
                        # LOGS:
                        #   05:38:29.363 - __main__:on_gui_message:56 - DEBUG - Msg: {"type": "mycroft.events.triggered", "namespace": "mycroft-weather.mycroftai", "event_name": "page_gained_focus", "data": {"number": 1}}
                        #   05:38:29.364 - __main__:on_gui_message:90 - ERROR - list index out of range
                        self.page = n[1][pos]

            self._draw_buffer()
            self.on_message(msg)
        except Exception as e:
            if self.debug:
                LOG.exception(e)
                LOG.error("Invalid JSON: " + str(payload))

    def on_message(self, message):
        pass

    def _draw_buffer(self):
        self.buffer = []
        if self.skill:
            self.buffer.append(
                bcolors.HEADER + "######################################" +
                bcolors.ENDC)
            self.buffer.append(
                bcolors.OKBLUE + "Active Skill:" + bcolors.ENDC + self.skill)

            if self.page:
                self.buffer.append(bcolors.OKBLUE + "Page:" + bcolors.ENDC +
                                   basename(self.page))
            else:
                self.buffer.append(bcolors.OKBLUE + "Page:" + bcolors.ENDC +
                                   bcolors.WARNING + "None" + bcolors.ENDC)

            if self.skill in self.vars:
                for v in dict(self.vars[self.skill]):
                    if self.vars[self.skill][v]:
                        self.buffer.append(bcolors.OKGREEN + "{}:".format(v)
                                           + bcolors.ENDC)
                        pretty = pformat(self.vars[self.skill][v])
                        for l in pretty.split("\n"):
                            self.buffer.append("    " + l)

    def draw(self):
        for line in self.buffer:
            print(line)


if __name__ == "__main__":
    gui = DummyGUI()
    gui.run()
