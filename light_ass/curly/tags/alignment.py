from __future__ import annotations

from dataclasses import dataclass

from ...utils import TypeParser
from .base import SimpleTag


def legacy2numpad(value: int) -> int:
        if value < 1 or value > 11:
            raise ValueError("Value must be between 1 and 11")
        value = value if value & 3 else 5
        if value > 8:
            value -= 1
        if value > 4:
            value -= 1
        return value


def numpad2legacy(value: int) -> int:
        if value < 1 or value > 9:
            raise ValueError("Value must be between 1 and 9")
        if value > 6:
            value += 2
        elif value > 3:
            value += 1
        return value


@dataclass
class AlignmentTag(SimpleTag[int]):
    tag_name = "an"
    _parse_param = staticmethod(TypeParser.parse_int)
    value: int | None

    @classmethod
    def from_legacy(cls, value: int) -> AlignmentTag:
        return AlignmentTag(legacy2numpad(value))


@dataclass
class LegacyAlignmentTag(SimpleTag[int]):
    tag_name = "a"
    _parse_param = staticmethod(TypeParser.parse_int)
    value: int | None

    @classmethod
    def from_numpad(cls, value: int) -> AlignmentTag:
        return AlignmentTag(numpad2legacy(value))
