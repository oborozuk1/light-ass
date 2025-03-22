from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Iterable

from .ass_types import AssTime
from .constants import OVERRIDE_BLOCK_PATTERN, DEFAULT_EVENTS_FORMAT
from .tag_parser import Tag, parse_tags
from .utils import to_snake_case

__all__ = [
    "Dialog",
    "Events",
]


@dataclass(kw_only=True)
class Dialog:
    text: str
    comment: bool = False
    layer: int = 0
    start: AssTime = field(default_factory=lambda: AssTime(0))
    end: AssTime = field(default_factory=lambda: AssTime(0))
    style: str = "Default"
    name: str = ""
    margin_l: int = 0
    margin_r: int = 0
    margin_v: int = 0
    effect: str = ""

    @property
    def start_time(self) -> AssTime:
        return self.start

    @start_time.setter
    def start_time(self, value: AssTime) -> None:
        self.start = value

    @property
    def end_time(self) -> AssTime:
        return self.end

    @end_time.setter
    def end_time(self, value: AssTime) -> None:
        self.end = value

    @property
    def actor(self) -> str:
        return self.name

    @actor.setter
    def actor(self, value: str) -> None:
        self.name = value

    @property
    def text_stripped(self) -> str:
        """
        Return the text of the event with override blocks removed.
        :return: The text of the event with override blocks removed.
        """
        return OVERRIDE_BLOCK_PATTERN.sub("", self.text)

    @classmethod
    def from_ass_line(cls, line: str, format_order: Iterable[str] | None = None):
        if format_order is None:
            format_order = DEFAULT_EVENTS_FORMAT

        kwargs = {"comment": line.startswith("Comment:")}
        _, _, line = line.partition(":")
        fields = line.split(",")
        for key, value in zip(format_order, fields):
            key = to_snake_case(key)
            value = value.strip()
            if key in ("start", "end"):
                value = AssTime(value)
            elif key in ("layer", "margin_l", "margin_r", "margin_v"):
                value = int(value)
            kwargs[key] = value

        return cls(**kwargs)

    def to_string(self) -> str:
        """
        Convert the Dialog object to a string.
        :return: A string representation of the Dialog object.
        """
        type_ = "Dialogue" if not self.comment else "Comment"
        return (f"{type_}: {self.layer},{self.start},{self.end},{self.style},{self.name},"
                f"{self.margin_l},{self.margin_r},{self.margin_v},{self.effect},{self.text}")

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

    def sort(self, *, key=None, reverse=False) -> None:
        """
        Sort the events in ascending order.
        :param key: A function that returns the value to sort by.
        :param reverse: Whether to sort in descending order.
        :return: None
        """
        if key is None:
            key = lambda x: x.start
        super().sort(key=key, reverse=reverse)
