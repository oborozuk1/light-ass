from __future__ import annotations

import math
from collections.abc import Iterator
from typing import Any, overload


class Point:
    __slots__ = ("x", "y")

    @overload
    def __init__(self, x: float, y: float) -> None: ...
    @overload
    def __init__(self, x: tuple[float, float]) -> None: ...
    @overload
    def __init__(self, x: complex) -> None: ...
    @overload
    def __init__(self, x: dict[str, float]) -> None: ...
    def __init__(self, x: Any, y: float | None = None) -> None:
        if y is None:
            if isinstance(x, complex):
                self.x = x.real
                self.y = x.imag
            elif isinstance(x, tuple):
                if len(x) != 2:
                    raise ValueError(f"Expected 2-tuple, got length {len(x)}")
                self.x = float(x[0])
                self.y = float(x[1])
            elif isinstance(x, dict):
                try:
                    self.x = float(x["x"])
                    self.y = float(x["y"])
                except KeyError as e:
                    raise ValueError(f"Missing key {e} in dict") from e
            else:
                raise TypeError(f"Cannot construct Point from {type(x).__name__}")
        else:
            self.x = float(x)
            self.y = float(y)

    def __iter__(self) -> Iterator[float]:
        yield self.x
        yield self.y

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Point):
            return self.x == other.x and self.y == other.y
        if isinstance(other, tuple) and len(other) == 2:
            ox: float = other[0]
            oy: float = other[1]
            return self.x == ox and self.y == oy
        if isinstance(other, complex):
            return self.x == other.real and self.y == other.imag
        return NotImplemented

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __repr__(self) -> str:
        return f"Point({self.x}, {self.y})"

    def __add__(self, other: Point | tuple[float, float]) -> Point:
        ox, oy = other
        return Point(self.x + ox, self.y + oy)

    def __sub__(self, other: Point | tuple[float, float]) -> Point:
        ox, oy = other
        return Point(self.x - ox, self.y - oy)

    def __mul__(self, scalar: float) -> Point:
        return Point(self.x * scalar, self.y * scalar)

    __rmul__ = __mul__

    def __neg__(self) -> Point:
        return Point(-self.x, -self.y)

    def scale(self, factor_x: float, factor_y: float | None = None) -> None:
        if factor_y is None:
            factor_y = factor_x
        self.x *= factor_x
        self.y *= factor_y

    def distance_to(self, other: Point | tuple[float, float]) -> float:
        ox, oy = other
        return math.hypot(self.x - ox, self.y - oy)
