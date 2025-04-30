import math
from typing import Self

from .point import Point
from ..utils import clamp

__all__ = [
    "Curve",
]


class Curve:
    def __init__(self, a: Point | None = None, b: Point | None = None, c: Point | None = None, d: Point | None = None):
        self.a = a if a is not None else Point()
        self.b = b if b is not None else Point()
        self.c = c if c is not None else Point()
        self.d = d if d is not None else Point()

        a.id = "l"
        b.id = "b"
        c.id = "b"
        d.id = "b"

    def __repr__(self):
        return f"Curve({self.a}, {self.b}, {self.c}, {self.d})"

    def get_x_at_time(self, t: float) -> float:
        """Gets the X position of a point running through the bezier for the given time."""
        t = clamp(t, 0, 1)
        return (1 - t) ** 3 * self.a.x + 3 * (1 - t) ** 2 * t * self.b.x + 3 * (
                1 - t) * t ** 2 * self.c.x + t ** 3 * self.d.x

    def get_y_at_time(self, t: float) -> float:
        """Gets the Y position of a point running through the bezier for the given time."""
        t = clamp(t, 0, 1)
        return (1 - t) ** 3 * self.a.y + 3 * (1 - t) ** 2 * t * self.b.y + 3 * (
                1 - t) * t ** 2 * self.c.y + t ** 3 * self.d.y

    def get_point_at_time(self, t: float) -> Point:
        """Gets the X and Y position of a point running through the bezier for the given time."""
        t = clamp(t, 0, 1)
        return Point(self.get_x_at_time(t), self.get_y_at_time(t))

    get_p_at_time = get_point_at_time

    def flatten(self, len_: float | None = None, reduce: float = 1) -> list[Point]:
        """Flattens the bezier segment"""
        if len_ is None:
            len_ = self.get_length()
        len_ = math.floor(len_ / reduce + 0.5)
        lengths = self.get_arc_lengths(len_)
        points = [Point(self.a.x, self.a.y)]
        for i in range(1, len_):
            points.append(self.get_point_at_time(Curve.uniform_time(lengths, len_, i / len_)))
        points.append(Point(self.d.x, self.d.y))
        return points

    def point_is_in_curve(self, p: Point, tolerance: float = 2, precision: int = 100) -> float | bool:
        """Checks if the point is on the bezier segment"""
        a = self.a
        d = self.d
        if a.x == p.x and a.y == p.y:
            return 0.0
        if d.x == p.x and d.y == p.y:
            return 1.0
        length = self.get_length()
        lengths = self.get_arc_lengths(precision)
        t = 0
        while t <= 1:
            u = Curve.uniform_time(lengths, length, t)
            if self.get_point_at_time(u).distance(p) <= tolerance:
                return t
            t += 1 / precision
        return False

    def split(self, t: float) -> list[Self]:
        """Splits the bezier segment in two"""
        t = clamp(t, 0, 1)
        a, b, c, d = self.a, self.b, self.c, self.d
        v1 = a.lerp(b, t)
        v2 = b.lerp(c, t)
        v3 = c.lerp(d, t)
        v4 = v1.lerp(v2, t)
        v5 = v2.lerp(v3, t)
        v6 = v4.lerp(v5, t)
        return [
            Curve(a, v1, v4, v6),
            Curve(v6, v5, v3, d)
        ]

    def split_at_interval(self, t: float, u: float):
        """Splits the bezier segment given an interval"""
        t = clamp(t, 0, 1)
        u = clamp(u, 0, 1)
        if t > u:
            u, t = t, u
        x1, y1 = self.a.x, self.a.y
        x2, y2 = self.b.x, self.b.y
        x3, y3 = self.c.x, self.c.y
        x4, y4 = self.d.x, self.d.y
        t2 = t * t
        t3 = t2 * t
        mt = t - 1
        mt2 = mt * mt
        mt3 = mt2 * mt
        u2 = u * u
        u3 = u2 * u
        mu = u - 1
        mu2 = mu * mu
        mu3 = mu2 * mu
        tu = t * u
        a, b, c, d = Point(), Point(), Point(), Point()
        a.x = -mt3 * x1 + 3 * t * mt2 * x2 - 3 * t2 * mt * x3 + t3 * x4
        a.y = -mt3 * y1 + 3 * t * mt2 * y2 - 3 * t2 * mt * y3 + t3 * y4
        b.x = -1 * mt2 * mu * x1 + mt * (3 * tu - 2 * t - u) * x2 + t * (-3 * tu + t + 2 * u) * x3 + t2 * u * x4
        b.y = -1 * mt2 * mu * y1 + mt * (3 * tu - 2 * t - u) * y2 + t * (-3 * tu + t + 2 * u) * y3 + t2 * u * y4
        c.x = -1 * mt * mu2 * x1 + mu * (3 * tu - t - 2 * u) * x2 + u * (-3 * tu + 2 * t + u) * x3 + t * u2 * x4
        c.y = -1 * mt * mu2 * y1 + mu * (3 * tu - t - 2 * u) * y2 + u * (-3 * tu + 2 * t + u) * y3 + t * u2 * y4
        d.x = -mu3 * x1 + 3 * u * mu2 * x2 - 3 * u2 * mu * x3 + u3 * x4
        d.y = -mu3 * y1 + 3 * u * mu2 * y2 - 3 * u2 * mu * y3 + u3 * y4
        return Curve(a, b, c, d)

    def get_coefficient(self) -> list[Point]:
        """Gets the cubic coefficient of the bezier segment"""
        a, b, c, d = self.a, self.b, self.c, self.d
        return [
            Point(d.x - a.x + 3 * (b.x - c.x), d.y - a.y + 3 * (b.y - c.y)),
            Point(3 * a.x - 6 * b.x + 3 * c.x, 3 * a.y - 6 * b.y + 3 * c.y),
            Point(3 * (b.x - a.x), 3 * (b.y - a.y)),
            Point(a.x, a.y)
        ]

    def get_derivative(self, t: float, cf=None) -> Point:
        """Gets the cubic derivative of the bezier segment"""
        if cf is None:
            cf = self.get_coefficient()
        a, b, c, _ = cf
        x = c.x + t * (2 * b.x + 3 * a.x * t)
        y = c.y + t * (2 * b.y + 3 * a.y * t)
        return Point(x, y)

    def get_normalized(self, t: float, inverse: bool = False) -> tuple[Point, Point, float]:
        """Gets the normalized tangent given a time on a bezier segment"""
        t = clamp(t, 0, 1)
        n = self.get_length()
        u = Curve.uniform_time(self.get_arc_lengths(n), n, t)
        p = self.get_p_at_time(u)
        tan = self.get_derivative(u)
        if inverse:
            tan.x, tan.y = tan.y, -tan.x
        else:
            tan.x, tan.y = -tan.y, tan.x
        mag = tan.vec_magnitude()
        tan.x /= mag
        tan.y /= mag
        return tan, p, u

    def get_length(self, t: float = 1) -> float:
        """Gets the real length of the segment through time"""
        abscissas = [
            -0.0640568928626056299791002857091370970011, 0.0640568928626056299791002857091370970011,
            -0.1911188674736163106704367464772076345980, 0.1911188674736163106704367464772076345980,
            -0.3150426796961633968408023065421730279922, 0.3150426796961633968408023065421730279922,
            -0.4337935076260451272567308933503227308393, 0.4337935076260451272567308933503227308393,
            -0.5454214713888395626995020393223967403173, 0.5454214713888395626995020393223967403173,
            -0.6480936519369755455244330732966773211956, 0.6480936519369755455244330732966773211956,
            -0.7401241915785543579175964623573236167431, 0.7401241915785543579175964623573236167431,
            -0.8200019859739029470802051946520805358887, 0.8200019859739029470802051946520805358887,
            -0.8864155270044010714869386902137193828821, 0.8864155270044010714869386902137193828821,
            -0.9382745520027327978951348086411599069834, 0.9382745520027327978951348086411599069834,
            -0.9747285559713094738043537290650419890881, 0.9747285559713094738043537290650419890881,
            -0.9951872199970213106468008845695294439793, 0.9951872199970213106468008845695294439793,
        ]
        weights = [
            0.1279381953467521593204025975865079089999, 0.1279381953467521593204025975865079089999,
            0.1258374563468283025002847352880053222179, 0.1258374563468283025002847352880053222179,
            0.1216704729278033914052770114722079597414, 0.1216704729278033914052770114722079597414,
            0.1155056680537255991980671865348995197564, 0.1155056680537255991980671865348995197564,
            0.1074442701159656343712356374453520402312, 0.1074442701159656343712356374453520402312,
            0.0976186521041138843823858906034729443491, 0.0976186521041138843823858906034729443491,
            0.0861901615319532743431096832864568568766, 0.0861901615319532743431096832864568568766,
            0.0733464814110802998392557583429152145982, 0.0733464814110802998392557583429152145982,
            0.0592985849154367833380163688161701429635, 0.0592985849154367833380163688161701429635,
            0.0442774388174198077483545432642131345347, 0.0442774388174198077483545432642131345347,
            0.0285313886289336633705904233693217975087, 0.0285313886289336633705904233693217975087,
            0.0123412297999872001830201639904771582223, 0.0123412297999872001830201639904771582223,
        ]

        t = clamp(t, 0, 1)
        len_, cf, z = 0, self.get_coefficient(), t / 2
        for abscissa, weight in zip(abscissas, weights):
            drv = self.get_derivative(z * abscissa + z, cf)
            len_ += weight * drv.hypot()
        return len_ * z

    def get_arc_lengths(self, precision: float = 100) -> list[float]:
        z = 1 / precision
        lengths, clen = [0.0], 0
        cx, cy = self.get_x_at_time(0), self.get_y_at_time(0)
        for i in range(1, int(precision) + 1):
            px, py = self.get_x_at_time(i * z), self.get_y_at_time(i * z)
            dx, dy = cx - px, cy - py
            cx, cy = px, py
            clen += math.sqrt(dx * dx + dy * dy)
            lengths.append(clen)
        return lengths

    @staticmethod
    def uniform_time(lengths, len_, u):
        target_length = u * lengths[-1]
        low, high, index = 0, len_, 0
        while low < high:
            index = int((low + high) / 2)
            if lengths[index + 1] < target_length:
                low = index + 1
            else:
                high = index
        if lengths[index + 1] > target_length:
            index = -1
        length_before = lengths[index + 1]
        if length_before == target_length:
            return index / len_
        return (index + 1) / len_ + (target_length - length_before) / (lengths[index + 1] - lengths[index]) * (1 / len_)

    def reverse(self):
        a2, b2, c2, d2 = self.a.copy(), self.b.copy(), self.c.copy(), self.d.copy()
        self.a, self.b, self.c, self.d = d2, c2, b2, a2
        self.a.id = "l"
        self.d.id = "b"
