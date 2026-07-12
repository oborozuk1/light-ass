from __future__ import annotations

import re

from .command import (
    BaseDrawCmd,
    BezierCmd,
    BSplineCmd,
    CloseCmd,
    ExtendSplineCmd,
    LineCmd,
    MoveCmd,
    MoveNoClosingCmd,
)
from .point import Point

CMD_PATTERN: re.Pattern[str] = re.compile(r"([cmnlbsp])")


class AssShape:
    def __init__(
        self, commands: list[BaseDrawCmd] | None = None, *, decimal: int = 3, raw: str | None = None
    ) -> None:
        self._parsed = commands is not None
        self._commands = commands if commands is not None else []
        self._raw = raw
        self.decimal = decimal

    def _parse(self) -> None:
        if self._parsed:
            return
        self._parsed = True
        if self._raw is None:
            return

        from ...utils import TypeParser

        def get_point(s: str) -> Point | None:
            try:
                x, pos = TypeParser.parse_float_with_pos(s, True)
                y, _ = TypeParser.parse_float_with_pos(s, True, pos)
                return Point(x, y)
            except ValueError:
                return None

        def get_points(s: str) -> list[Point]:
            pos = 0
            res = []
            while pos < len(s):
                try:
                    x, pos = TypeParser.parse_float_with_pos(s, True, pos)
                    y, pos = TypeParser.parse_float_with_pos(s, True, pos)
                    res.append(Point(x, y))
                except ValueError:
                    break
            return res


        command_type_map = {
            "m": MoveCmd,
            "n": MoveNoClosingCmd,
            "l": LineCmd,
            "b": BezierCmd,
            "s": BSplineCmd,
            "p": ExtendSplineCmd,
            "c": CloseCmd,
        }

        commands = []
        started = False
        parts = CMD_PATTERN.split(self._raw)
        for cmd, points_str in zip(parts[1::2], parts[2::2], strict=False):
            cmd_type = command_type_map[cmd]
            match cmd:
                case "m" | "n":
                    point = get_point(points_str)
                    if point is None:
                        continue
                    started = True
                    commands.append(cmd_type(point))
                case "l" | "b" | "s" | "p":
                    if not started:
                        continue
                    points = get_points(points_str)
                    commands.append(cmd_type(points))
                case "c":
                    commands.append(cmd_type())
        self._commands = commands

    @classmethod
    def from_ass(cls, shape: str) -> AssShape:
        return cls(raw=shape)

    @property
    def commands(self) -> list[BaseDrawCmd]:
        self._parse()
        return self._commands

    @commands.setter
    def commands(self, commands: list[BaseDrawCmd]) -> None:
        self._commands = commands
        self._parsed = True

    def scale(self, factor_x: float, factor_y: float | None = None) -> None:
        if factor_y is None:
            factor_y = factor_x
        for command in self.commands:
            if isinstance(command, (MoveCmd, MoveNoClosingCmd)):
                command.point.scale(factor_x, factor_y)
            elif isinstance(command, (LineCmd, BezierCmd, BSplineCmd, ExtendSplineCmd)):
                for point in command.points:
                    point.scale(factor_x, factor_y)

    def to_ass(self, decimal: int | None = None) -> str:
        if decimal is None and not self._parsed and self._raw:
            return self._raw
        if decimal is None:
            decimal = self.decimal
        return " ".join(c.serialize(decimal) for c in self.commands)

    def __repr__(self) -> str:
        if not self._parsed:
            return "AssShape(unparsed)"
        return (
            f"AssShape(with {len(self.commands)} command{'s' if len(self.commands) != 1 else ''})"
        )
