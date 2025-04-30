import math
from typing import Self, Literal

__all__ = [
    "Point",
]


class Point:
    def __init__(self, x: float = 0, y: float = 0, id_: Literal["m", "l", "b"] | str = "l"):
        self.x = x
        self.y = y
        self.id = id_

    def __repr__(self):
        return f"Point({self.id}, {self.x}, {self.y})"

    def __add__(self, other: float | tuple[float, float] | Self) -> Self:
        if isinstance(other, (int, float)):
            return Point(self.x + other, self.y + other)
        elif isinstance(other, tuple) and len(other) == 2:
            return Point(self.x + other[0], self.y + other[1])
        elif isinstance(other, Point):
            return Point(self.x + other.x, self.y + other.y)
        else:
            raise TypeError("unsupported operand type")

    def __sub__(self, other: float | tuple[float, float] | Self) -> Self:
        if isinstance(other, (int, float)):
            return Point(self.x - other, self.y - other)
        elif isinstance(other, tuple) and len(other) == 2:
            return Point(self.x - other[0], self.y - other[1])
        elif isinstance(other, Point):
            return Point(self.x - other.x, self.y - other.y)
        else:
            raise TypeError("unsupported operand type")

    def __mul__(self, other: float | tuple[float, float] | Self) -> Self:
        if isinstance(other, (int, float)):
            return Point(self.x * other, self.y * other)
        elif isinstance(other, tuple) and len(other) == 2:
            return Point(self.x * other[0], self.y * other[1])
        elif isinstance(other, Point):
            return Point(self.x * other.x, self.y * other.y)
        else:
            raise TypeError("unsupported operand type")

    def __truediv__(self, other: float | tuple[float, float] | Self) -> Self:
        if isinstance(other, (int, float)):
            return Point(self.x / other, self.y / other)
        elif isinstance(other, tuple) and len(other) == 2:
            return Point(self.x / other[0], self.y / other[1])
        elif isinstance(other, Point):
            return Point(self.x / other.x, self.y / other.y)
        else:
            raise TypeError("unsupported operand type")

    def __neg__(self):
        return Point(-self.x, -self.y)

    def __eq__(self, other: Self) -> bool:
        if not isinstance(other, Point):
            return self.x == other.x and self.y == other.y
        return False

    def copy(self) -> Self:
        return Point(self.x, self.y, self.id)

    def move(self, x: float = 0, y: float = 0) -> None:
        """Moves the object according the given params."""
        self.x += x
        self.y += y

    def rotate(self, angle: float, c: Self | None = None) -> None:
        """Rotates the object according the given params."""
        if c is None:
            c = Point(0, 0)
        x_rel = self.x - c.x
        y_rel = self.y - c.y
        self.x = x_rel * math.cos(angle) - y_rel * math.sin(angle) + c.x
        self.y = x_rel * math.sin(angle) + y_rel * math.cos(angle) + c.y

    def rotate_frz(self, angle: float) -> None:
        """Rotates the object according the given params."""
        angle = math.radians(angle)
        self.rotate(-angle)

    def scale(self, hor: float = 100, ver: float = 100) -> None:
        """Scales the object according the given params."""
        self.x *= hor / 100
        self.y *= ver / 100

    def round(self, n: int = 3) -> None:
        """Rounds the coordinates of the point."""
        self.x = round(self.x, n)
        self.y = round(self.y, n)

    def lerp(self, point: Self, t: float) -> Self:
        """Linear interpolation between two points"""
        return Point((1 - t) * self.x + t * point.x, (1 - t) * self.y + t * point.y)

    def sq_distance(self, point: Self) -> float:
        """Squared distance between two points"""
        return (self.x - point.x) ** 2 + (self.y - point.y) ** 2

    def distance(self, point: Self) -> float:
        """Distance between two points"""
        return math.sqrt(self.sq_distance(point))

    def angle(self, point: Self | None = None) -> float:
        """Angle between two points"""
        if point is None:
            return math.atan2(self.y, self.x)
        return math.atan2(point.y - self.y, point.x - self.x)

    def dot(self, point: Self) -> float:
        """Returns the dot product of the point and another point."""
        return self.x * point.x + self.y * point.y

    def cross(self, point: Self) -> float:
        """Returns the cross product of the point and another point."""
        return self.x * point.y - self.y * point.x

    def vec_length(self) -> float:
        """Calculates the length of the vector."""
        return self.x ** 2 + self.y ** 2

    def vec_magnitude(self) -> float:
        """Calculates the magnitude of the vector."""
        return math.sqrt(self.vec_length())

    def vec_normalize(self) -> Self:
        """Normalizes the coordinates of the vector."""
        length = self.vec_length()
        if length == 0:
            return Point(0, 0)
        return Point(self.x / length, self.y / length)

    def vec_scale(self, len_: float) -> Self:
        """Scales the coordinates of the vector."""
        length = self.vec_length()
        if length == 0:
            return Point(0, 0)
        return Point(self.x * len_ / length, self.y * len_ / length)

    def sq_seg_distance(self, p1: Self, p2: Self) -> float:
        """Squared distance between a point and a segment"""
        x, y = p1.x, p1.y
        dx = p2.x - x
        dy = p2.y - y
        if dx != 0 or dy != 0:
            t = ((self.x - x) * dx + (self.y - y) * dy) / (dx * dx + dy * dy)
            if t > 1:
                x, y = p2.x, p2.y
            elif t > 0:
                x += dx * t
                y += dy * t
        return self.sq_distance(Point(x, y))

    def seg_distance(self, p1: Self, p2: Self) -> float:
        """Distance between a point and a segment"""
        return math.sqrt(self.sq_seg_distance(p1, p2))

    def hypot(self) -> float:
        """Distance between the origin and the point"""
        if self.x == 0 and self.y == 0:
            return 0
        ax, ay = math.fabs(self.x), math.fabs(self.y)
        px, py = max(ax, ay), min(ax, ay)
        return px * math.sqrt(1 + (py / px) ** 2)

    def quad_PT2UV(self, a: Self, b: Self, c: Self, d: Self) -> Self:
        """Maps a point from XY coordinates to UV coordinates on a quadrilateral surface."""
        e = Point(b.x - a.x, b.y - a.y)
        f = Point(d.x - a.x, d.y - a.y)
        g = Point(a.x - b.x + c.x - d.x, a.y - b.y + c.y - d.y)
        h = Point(self.x - a.x, self.y - a.y)

        k2 = g.cross(f)
        k1 = e.cross(f) + h.cross(g)
        k0 = h.cross(e)

        if math.fabs(k2) < 1e3:
            u = (h.x * k1 + f.x * k0) / (e.x * k1 - g.x * k0)
            v = -k0 / k1
            return Point(u, v)

        w = k1 * k1 - 4 * k0 * k2
        if w < 0:
            return Point(-1, -1)
        w = math.sqrt(w)

        ik2 = 0.5 / k2
        v = (-k1 - w) * ik2
        u = (h.x - f.x * v) / (e.x + g.x * v)

        if u < 0 or u > 1 or v < 0 or v > 1:
            v = (-k1 + w) * ik2
            u = (h.x - f.x * v) / (e.x + g.x * v)

        return Point(u, v)

    def quad_UV2PT(self, a: Self, b: Self, c: Self, d: Self) -> Self:
        """Does the inverse of quadPT2UV."""
        u, v = self.x, self.y
        px = a.x + u * (b.x - a.x) + v * (d.x - a.x) + u * v * (a.x - b.x + c.x - d.x)
        py = a.y + u * (b.y - a.y) + v * (d.y - a.y) + u * v * (a.y - b.y + c.y - d.y)
        return Point(px, py)
