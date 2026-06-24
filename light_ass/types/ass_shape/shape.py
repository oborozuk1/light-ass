from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import ClassVar

__all__ = [
    "AssShape",
]


@dataclass(slots=True)
class Point:
    x: float
    y: float


@dataclass(slots=True)
class Command:
    cmd: str
    points: list[Point]

    def to_ass(self, decimal: int | None = None) -> str:
        from ...utils import Formatter

        fmt = Formatter.format_float
        points_str = " ".join(f"{fmt(p.x, decimal)} {fmt(p.y, decimal)}" for p in self.points)
        return f"{self.cmd} {points_str}"


@dataclass(slots=True, init=False)
class AssShape:
    COMMAND_PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        r"([mlbpc])(\s+[+-]?\d*\.?\d*(?:[eE][+-]?\d+)?\s+[+-]?\d*\.?\d*(?:[eE][+-]?\d+)?)*",
        re.ASCII,
    )

    decimal: int
    _commands: list[Command] = field(repr=False, compare=False)
    _raw: str | None = field(repr=False, compare=False)
    _parsed: bool = field(repr=False, compare=False)

    def __init__(
        self, commands: list[Command] | None = None, *, decimal: int = 3, raw: str | None = None
    ) -> None:
        self._parsed = commands is not None
        if commands is None:
            commands = []
        self._commands = commands
        self._raw = raw
        self.decimal = decimal

    def _parse(self) -> None:
        if self._parsed:
            return
        self._parsed = True
        commands = []
        for match in self.COMMAND_PATTERN.finditer(self._raw or ""):
            groups = match.groups()
            cmd = groups[0]
            points = []
            for point in groups[1:]:
                parts = point.split()
                x, y = map(float, parts)
                points.append(Point(x, y))
            commands.append(Command(cmd, points))
        self._commands = commands

    @classmethod
    def from_ass(cls, shape: str) -> AssShape:
        return cls(raw=shape)

    @property
    def commands(self) -> list[Command]:
        self._parse()
        return self._commands

    @commands.setter
    def commands(self, commands: list[Command]) -> None:
        self._commands = commands
        self._parsed = True

    def scale(self, factor_x: float, factor_y: float | None = None) -> None:
        if factor_y is None:
            factor_y = factor_x
        for command in self._commands:
            for point in command.points:
                point.x *= factor_x
                point.y *= factor_y

    def to_ass(self, decimal: int | None = None) -> str:
        if decimal is None:
            decimal = self.decimal
        return " ".join(c.to_ass(decimal) for c in self.commands)

    def __repr__(self) -> str:
        if not self._parsed:
            return "AssShape(unparsed)"
        return (
            f"AssShape(with {len(self.commands)} command{'s' if len(self.commands) != 1 else ''})"
        )
