import math
from typing import Self

from .point import Point
from ..utils import clamp

__all__ = [
    "Segment",
]


class Segment:
    def __init__(self, a: Point | None = None, b: Point | None = None):
        self.a = a if a is not None else Point()
        self.b = b if b is not None else Point()

    def get_x_at_time(self, t: float) -> float:
        """Gets the value of X given a time on a segment"""
        return (1 - t) * self.a.x + t * self.b.x

    def get_y_at_time(self, t: float) -> float:
        """Gets the value of Y given a time on a segment"""
        return (1 - t) * self.a.y + t * self.b.y

    def get_point_at_time(self, t: float) -> Point:
        """Gets the value of Point given a time on a segment"""
        return Point(self.get_x_at_time(t), self.get_y_at_time(t))

    get_p_at_time = get_point_at_time

    def flatten(self, len_: float | None = None, reduce: float = 1) -> list[Point]:
        """Flattens the segment"""
        len_ = math.floor(len_ / reduce + 0.5)
        points = [Point(self.a.x, self.a.y)]
        for i in range(1, len_):
            points.append(self.get_point_at_time(i / len_))
        points.append(Point(self.b.x, self.b.y))
        return points

    def split(self, t: float = 0.5) -> list[Self]:
        """Splits the segment in two"""
        a, b = self.a, self.b
        c = a.lerp(b, t)
        return [
            Segment(a, c),
            Segment(c, b)
        ]

    def get_normalized(self, t: float, inverse: bool = False) -> tuple[Point, Point, float]:
        """Gets the normalized tangent given a time on a segment"""
        t = clamp(t, 0, 1)
        p = self.get_point_at_time(t)
        d = Point()
        d.x = self.b.x - p.x
        d.y = self.b.y - p.y
        if inverse:
            d.x, d.y = d.y, -d.x
        else:
            d.x, d.y = -d.y, d.x
        mag = d.vec_magnitude()
        tan = Point(d.x / mag, d.y / mag)
        return tan, p, t

    def get_length(self, t: float = 1) -> float:
        """Gets the real length of the segment through time"""
        return t * self.a.distance(self.b)

    def line_to_bezier(self) -> tuple[Point, Point, Point, Point]:
        """Converts a segment to a bezier curve"""
        a = self.a.copy()
        b = Point((2 * self.a.x + self.b.x) / 3, (2 * self.a.y + self.b.y) / 3)
        c = Point((self.a.x + 2 * self.b.x) / 3, (self.a.y + 2 * self.b.y) / 3)
        d = self.b.copy()
        a.id, b.id, c.id, d.id = "l", "b", "b", "b"
        return a, b, c, d

    def reverse(self) -> None:
        a2 = self.a.copy()
        b2 = self.b.copy()
        self.a = b2
        self.b = a2
