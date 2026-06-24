from __future__ import annotations

import re
from dataclasses import dataclass
from typing import ClassVar


@dataclass(slots=True)
class AssTime:
    ASS_TIME_PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        r"(\d+):(\d+):(\d+).(\d+)", flags=re.ASCII
    )
    time: int

    @classmethod
    def parse(cls, s: str) -> AssTime:
        hours, minutes, seconds_ms = s.split(":")
        seconds, milliseconds = seconds_ms.split(".", maxsplit=1)
        return cls(
            int(hours) * 3600000
            + int(minutes) * 60000
            + int(seconds) * 1000
            + int(milliseconds.ljust(3, "0"))
        )

    def to_ass(self) -> str:
        ms = max(0, int(round(self.time)))
        h, ms = divmod(ms, 3600000)
        m, ms = divmod(ms, 60000)
        s, ms = divmod(ms, 1000)
        return f"{h:01d}:{m:02d}:{s:02d}.{round(ms / 10):02d}"

    def __repr__(self) -> str:
        return f"AssTime({self.time})"

    def __str__(self) -> str:
        return self.to_ass()

    def __int__(self) -> int:
        return self.time

    def __hash__(self) -> int:
        return hash(self.time)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, AssTime):
            return self.time == other.time
        if isinstance(other, (int, float)):
            return self.time == int(other)
        return NotImplemented

    def __lt__(self, other: AssTime | int | float) -> bool:
        if isinstance(other, AssTime):
            return self.time < other.time
        if isinstance(other, (int, float)):
            return self.time < int(other)
        return NotImplemented

    def __le__(self, other: AssTime | int | float) -> bool:
        if isinstance(other, AssTime):
            return self.time <= other.time
        if isinstance(other, (int, float)):
            return self.time <= int(other)
        return NotImplemented

    def __gt__(self, other: AssTime | int | float) -> bool:
        if isinstance(other, AssTime):
            return self.time > other.time
        if isinstance(other, (int, float)):
            return self.time > int(other)
        return NotImplemented

    def __ge__(self, other: AssTime | int | float) -> bool:
        if isinstance(other, AssTime):
            return self.time >= other.time
        if isinstance(other, (int, float)):
            return self.time >= int(other)
        return NotImplemented

    def __add__(self, other: AssTime | int | float) -> AssTime:
        if isinstance(other, AssTime):
            return AssTime(self.time + other.time)
        if isinstance(other, (int, float)):
            return AssTime(self.time + int(other))
        return NotImplemented

    def __radd__(self, other: int | float) -> AssTime:
        return self.__add__(other)

    def __iadd__(self, other: AssTime | int | float) -> AssTime:
        if isinstance(other, AssTime):
            self.time += other.time
        elif isinstance(other, (int, float)):
            self.time += int(other)
        else:
            return NotImplemented
        return self

    def __sub__(self, other: AssTime | int | float) -> AssTime:
        if isinstance(other, AssTime):
            return AssTime(self.time - other.time)
        if isinstance(other, (int, float)):
            return AssTime(self.time - int(other))
        return NotImplemented

    def __rsub__(self, other: int | float) -> AssTime:
        return AssTime(int(other)) - self

    def __isub__(self, other: AssTime | int | float) -> AssTime:
        if isinstance(other, AssTime):
            self.time -= other.time
        elif isinstance(other, (int, float)):
            self.time -= int(other)
        else:
            return NotImplemented
        return self

    def __mul__(self, other: int | float) -> AssTime:
        if isinstance(other, (int, float)):
            return AssTime(int(self.time * other))
        return NotImplemented

    def __rmul__(self, other: int | float) -> AssTime:
        return self.__mul__(other)

    def __truediv__(self, other: int | float) -> float:
        if isinstance(other, (int, float)):
            return self.time / other
        return NotImplemented

    def __floordiv__(self, other: int | float) -> AssTime:
        if isinstance(other, (int, float)):
            return AssTime(int(self.time // other))
        return NotImplemented
