from __future__ import annotations

from enum import IntEnum


def legacy2numpad(value: int) -> int:
    if value < 1 or value > 11:
        raise ValueError("Value must be between 1 and 11")
    value = value if value & 3 else 5
    if value > 8:
        return value - 5
    if value > 4:
        return value + 2
    return value


def numpad2legacy(value: int) -> int:
    if value < 1 or value > 9:
        raise ValueError("Value must be between 1 and 9")
    if value > 6:
        return value - 2
    if value > 3:
        return value + 5
    return value


class Align(IntEnum):
    BOTTOM_LEFT   = 1
    BOTTOM_CENTER = 2
    BOTTOM_RIGHT  = 3
    MID_LEFT      = 4
    MID_CENTER    = 5
    MID_RIGHT     = 6
    TOP_LEFT      = 7
    TOP_CENTER    = 8
    TOP_RIGHT     = 9

    @classmethod
    def from_legacy(cls, value: int) -> Align:
        return cls(legacy2numpad(value))

    @property
    def legacy(self) -> int:
        return numpad2legacy(self.value)

    def is_left(self) -> bool:
        return self.value in (1, 4, 7)

    def is_center(self) -> bool:
        return self.value in (2, 5, 8)

    def is_right(self) -> bool:
        return self.value in (3, 6, 9)

    def is_top(self) -> bool:
        return self.value in (7, 8, 9)

    def is_mid(self) -> bool:
        return self.value in (4, 5, 6)

    def is_bottom(self) -> bool:
        return self.value in (1, 2, 3)
