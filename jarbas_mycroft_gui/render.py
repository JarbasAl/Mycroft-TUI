import pprint
from rich import print
from rich.columns import Columns
from rich.panel import Panel
from rich.console import Console
from rich.style import Style
from art import text2art
from jarbas_mycroft_gui.settings import TITLE_FONT
from collections.abc import Iterable


class RichDraw(Console):

    info = Style(color="cyan", blink=False, bold=False)
    message = Style(color="blue", blink=False, bold=False)
    warn = Style(color="yellow", blink=False, bold=True)
    danger = Style(color="red", blink=True, bold=True)

    def __init__(self):
        super().__init__(record=True)

    def _check_buffer(self) -> None:
        """Check if the buffer may be rendered."""
        if self._buffer_index == 0:
            text = self._render_buffer()


def pretty_var(var, data, return_str=True):
    data_str = pprint.pformat(data, indent=4) or str(data)

    # NOTE lists mess rich formatting because of [ ] syntax
    data_str = data_str.replace("[", "(").replace("]", ")")

    if isinstance(data, Iterable):
        # remove first set of [] / {} / ()
        data_str = data_str[1:-1]
        # draw markers between vars
        size = max([len(l.strip()) for l in data_str.split("\n")]) - 1
        marker = "\n" + "_" * size + "\n"
        data_str = data_str.replace(",\n", "," + marker)
        # indent dicts
        data_str = data_str.replace("{", "{\n" + " " * 4)
        data_str = data_str.replace("}", "\n}")

    # normalize indent
    data_str = "\n".join([" " * 2 + l.strip() for l in data_str.split("\n")])

    rich_formated = f"[b]{var}[/b]\n[yellow]{data_str}[yellow]"

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


def pretty_print(log, style=RichDraw.info):
    canvas = RichDraw()
    canvas.print(log, style=style)
    return canvas.export_text(styles=True)


if __name__ == "__main__":
    vars = {
        "a": "b",
        "foo": ["list", "of", "things"],
        "fooo": ["list", "of", "more", "like", "a", "lot", "of",
                 "small", "things", "just", "enough", "to", "force",
                 "multiple", "lines"],
        "foooooo": [{'age': 4.779999999999986,
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
                     'water': 99.66805555555699},
                    {'age': 4.779999999999986,
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
                     'water': 99.66805555555699}
            , {'age': 4.779999999999986,
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
               'water': 99.66805555555699}],
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

    print(pretty_print("everything fine"))
    print(pretty_print("this seems wrong",
                       RichDraw.message))
    print(pretty_print("warning, bad thing happened",
                       RichDraw.warn))
    print(pretty_print("division by zero, hacked too much time",
                       RichDraw.danger))
    print(pretty_title("This is the Title", font="small"))

    print(pretty_dict(vars))
