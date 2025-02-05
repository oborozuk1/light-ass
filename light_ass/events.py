from collections.abc import Sequence

from .ass_types import AssTime
from .constants import OVERRIDE_BLOCK_PATTERN
from .tag_parser import Tag, parse_tags
from .utils import validate_value


class Dialog(dict):
    _formats = {
        "comment": bool,
        "layer": int,
        "start": AssTime,
        "end": AssTime,
        "style": str,
        "name": str,
        "margin_l": int,
        "margin_r": int,
        "margin_v": int,
        "effect": str,
        "text": str,
    }
    _alias = {
        "commented": "comment",
        "start_time": "start",
        "end_time": "end",
        "actor": "name",
    }

    comment: bool
    layer: int
    start: AssTime
    end: AssTime
    style: str
    name: str
    margin_l: int
    margin_r: int
    margin_v: int
    effect: str
    text: str
    commented: bool
    start_time: AssTime
    end_time: AssTime
    actor: str

    def __init__(self, **kwargs) -> None:
        if set(kwargs.keys()) != set(self._formats.keys()):
            raise ValueError("Keys of kwargs must equal formats")
        super().__init__()
        for key, value in kwargs.items():
            self[key] = self.validate_value(key, value)

    def __getattr__(self, name: str):
        if name in self._alias:
            name = self._alias[name]
        if name in self._formats:
            return self[name]
        else:
            raise AttributeError(f"{name} is not a valid attribute")

    def __setattr__(self, name: str, value):
        if name in self._alias:
            name = self._alias[name]
        if name in self._formats:
            self[name] = Dialog.validate_value(name, value)
        else:
            raise AttributeError(f"{name} is not a valid attribute")

    def __repr__(self) -> str:
        return "Dialog({})".format(
            ",".join(f"{key}={value}" for key, value in self.items())
        )

    def __str__(self) -> str:
        dialog_line = []
        for key, value in self.items():
            if key == "comment":
                continue
            if type(value) is float:
                value = f"{value:g}"
            dialog_line.append(str(value))
        return "{}: {}".format("Comment" if self.comment else "Dialogue", ",".join(dialog_line))

    def shift(self, ms: int) -> None:
        """
        Shift the start and end time of the event by milliseconds.
        :param ms: The amount of milliseconds to shift the event by.
        :return: None
        """
        self.start += ms
        self.end += ms

    def parse_tags(self) -> list[Tag]:
        """
        Parse the tags in the text of the event.
        :return: A list of Tag objects.
        """
        return parse_tags(self.text)

    @property
    def text_stripped(self) -> str:
        """
        Return the text of the event with override blocks removed.
        :return: The text of the event with override blocks removed.
        """
        return OVERRIDE_BLOCK_PATTERN.sub("", self.text)

    @staticmethod
    def validate_value(key, value):
        if key in Dialog._alias:
            key = Dialog._alias[key]
        try:
            return validate_value(Dialog._formats[key], value)
        except ValueError:
            raise ValueError(f"Invalid value for {key}: {value}")


class Events(list[Dialog]):
    def pop(self, index: int | Sequence[int] = -1) -> None:
        """
        Remove the event at the specified index.
        :param index: The index of the event to remove, or a sequence of indices.
        :return: None
        """
        if isinstance(index, int):
            index = (index,)
        for i in sorted(index, reverse=True):
            super().pop(i)

    def shift(self, ms: int, range_: Sequence[int] | None = None) -> None:
        """
        Shift the start and end time of events by milliseconds.
        :param ms: The amount of milliseconds to shift the events by.
        :param range_: The range of events to shift. If None, all events will be shifted.
        :return: None
        """
        if range_ is None:
            range_ = range(0, len(self))
        for i in range_:
            self[i].shift(ms)

    def sort(self, *, key = None, reverse = False) -> None:
        """
        Sort the events in ascending order.
        :param key: A function that returns the value to sort by.
        :param reverse: Whether to sort in descending order.
        :return: None
        """
        if key is None:
            key = lambda x: x.start
        super().sort(key = key, reverse = reverse)