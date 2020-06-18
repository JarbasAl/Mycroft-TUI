import pprint
from rich import print
from rich.columns import Columns
from rich.panel import Panel
from rich.console import Console
from art import text2art
from jarbas_mycroft_gui.settings import TITLE_FONT


class RichDraw(Console):
    def __init__(self):
        super().__init__(record=True)

    def _check_buffer(self) -> None:
        """Check if the buffer may be rendered."""
        if self._buffer_index == 0:
            text = self._render_buffer()


def pretty_var(var, data, return_str=True):
    """Extract text from user dict."""
    if isinstance(data, list) or \
            isinstance(data, tuple) or \
            isinstance(data, set):
        # NOTE lists mess format because of [ ] syntax
        data_str = pprint.pformat(data, indent=4) or str(data)
        data_str = data_str.replace("[", "(").replace("]", ")")
    else:
        data_str = pprint.pformat(data, indent=4) or str(data)
    rich_formated = f"[b]{var}[/b]\n[yellow]{data_str}"
    pretty = Panel(rich_formated, expand=True)
    if not return_str:
        return pretty
    canvas = RichDraw()
    canvas.print(pretty)
    return canvas.export_text()


def pretty_dict(data, return_str=True, ignored_keys=None):
    ignored_keys = ignored_keys or []
    pretty = Columns([pretty_var(k, data[k], return_str=False)
                      for k in data if k not in ignored_keys])
    if not return_str:
        return pretty
    canvas = RichDraw()
    canvas.print(pretty)
    return canvas.export_text()


def pretty_title(title, font=TITLE_FONT):
    return text2art(title, font=font).replace("\r", "")


if __name__ == "__main__":
    vars = {
        "a": "b",
        "foo": ["list", "of", "things"],
        "bar": {"bar_A": "a",
                "bar_B": 1,
                "bar_C": ["c"],
                "bar_D": {"jarbas": "mycroft"},
                "PET": {'age': 4.779999999999986,
                        'birthday': '2020-06-16 23:49:40.967524',
                        'energy': 99.66805555555699,
                        'food': 99.66805555555699,
                        'happiness': 99.66805555555699,
                        'health': 100,
                        'hygiene': 99.64444444444574,
                        'is_dead': False,
                        'is_playing': False,
                        'is_sick': False,
                        'is_sleeping': False,
                        'poo': 1,
                        'water': 99.66805555555699}}
    }



    fonts = ["stampatello", "standard", "soft", "spliff", "smslant", "usa",
             "utopia", "varsity", "wavy", "weird", "3d_diagonal", "3x5",
             "5lineoblique", "64f1", "6x10", "6x9", "acrobatic", "big",
             "smscript", "stampate", "stacey", "stop", "straight", "sweet",
             "slscript", "small", "starwars", "univers"]

    title = text2art("This is the Title", font="small")
    print(type(title))
    print(title)

    print(pretty_dict(vars))