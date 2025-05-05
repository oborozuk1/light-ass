import math
import re
from collections.abc import Callable
from typing import Self, TypedDict, Any, Literal

from .curve import Curve
from .point import Point
from .segment import Segment
from ..utils import format_number

__all__ = [
    "Shape",
]


class BoundingBoxType(TypedDict):
    l: float
    t: float
    r: float
    b: float
    width: float
    height: float
    origin: Point
    center: Point
    ass_draw: str


class Shape:
    path: list[list[Point]]

    def __init__(self, shape: str | list[list[Point]] | Self | None = None):
        if shape is None:
            self.path = []
        elif isinstance(shape, str):
            self.path = self.import_shape(shape)
        elif isinstance(shape, list):
            self.path = [contour.copy() for contour in shape]
        elif isinstance(shape, Shape):
            self.path = shape.path
        else:
            raise ValueError("Unsupported type")

    def __repr__(self):
        return f"Shape(with {len(self.path)} path{'s' if len(self.path) != 1 else ''})"

    @classmethod
    def create_rectangle(cls, x1: float, y1: float, x2: float, y2: float) -> Self:
        return cls([[Point(x1, y1), Point(x2, y1), Point(x2, y2), Point(x1, y2)]])

    @staticmethod
    def import_shape(shape: str) -> list[list[Point]]:
        paths = []
        for str_path in re.findall(r"m [^m]+", shape):
            path = []
            paths.append(path)
            curr_cmd = None
            for match in re.finditer(r"([a-zA-Z]?)\s+(-?\d+(?:\.\d*)?)\s+(-?\d+(?:\.\d*)?)", str_path):
                cmd, x, y = match.groups()
                x = float(x)
                y = float(y)
                if cmd:
                    if not re.search(r"[mlb]", cmd):
                        raise ValueError("shape unknown")
                    curr_cmd = cmd
                path.append(Point(x, y, curr_cmd))
            if path:
                path[0].id = "l"
        return paths

    def export_shape(self, decimal: int = 2) -> str:
        shapes = []
        for contour in self.path:
            shape = []
            j = 1
            cmd = None
            while j < len(contour):
                curr = contour[j]
                if curr.id == "b":
                    c = contour[j + 1]
                    c.round(decimal)
                    if j + 2 < len(contour):
                        d = contour[j + 2]
                        d.round(decimal)
                    else:
                        d = Point()
                    if cmd != "b":
                        cmd = "b"
                        shape.append("b")
                    shape.append(" ".join(map(format_number, (curr.x, curr.y, c.x, c.y, d.x, d.y))))
                    j += 2
                else:
                    if cmd != "l":
                        cmd = "l"
                        shape.append("l")
                    shape.append(f"{format_number(curr.x)} {format_number(curr.y)}")
                j += 1
            shapes.append(f"m {format_number(contour[0].x)} {format_number(contour[0].y)} " + " ".join(shape))
        return "".join(shapes)

    to_string = export_shape

    def copy(self):
        return Shape(self)

    def map(self, fn: Callable[[float, float, Point], Any]) -> None:
        for contour in self.path:
            for point in contour:
                res = fn(point.x, point.y, point)
                if isinstance(res, Point):
                    px = res.x
                    py = res.y
                elif isinstance(res, tuple):
                    px, py = res
                else:
                    px = py = None
                if px is not None and py is not None:
                    point.x, point.y = px, py

    def callback_path(self, fn: Callable[[str, Curve | Segment, int], Any]) -> None:
        k = 0
        for contour in self.path:
            j = 1
            while j < len(contour):
                prev = contour[j - 1]
                curr = contour[j]
                if curr.id == "b":
                    if fn("b", Curve(prev, curr, contour[j + 1], contour[j + 2]), k) == "break":
                        return
                    j += 2
                else:
                    if fn("l", Segment(prev, curr), k) == "break":
                        return
                j += 1
            k += 1

    @property
    def bounding_box(self) -> BoundingBoxType:
        def fn(x, y, _):
            nonlocal l, t, r, b
            if x < l:
                l = x
            if y < t:
                t = y
            if x > r:
                r = x
            if y > b:
                b = y

        l, t, r, b = math.inf, math.inf, -math.inf, -math.inf
        self.map(fn)

        return {
            "l": l,
            "t": t,
            "r": r,
            "b": b,
            "width": r - l,
            "height": b - t,
            "origin": Point(l, t),
            "center": Point((l + r) / 2, (t + b) / 2),
            "ass_draw": f"m {l} {t} {r} {t} {r} {b} {l} {b}"
        }

    def flatten(self, distance: float = 1, flatten_straight: bool = False, custom_len: float | None = None):
        """Flattens bezier segments and optionally flattens line segments of the path"""
        new_path = []
        for contour in self.path:
            j = 1
            new_contour = [contour[0].copy()]
            while j < len(contour):
                prev = contour[j - 1]
                curr = contour[j]
                if curr.id == "b":
                    points = Curve(prev, curr, contour[j + 1], contour[j + 2]).flatten(custom_len, distance)
                    for k in range(1, len(points)):
                        new_contour.append(points[k])
                    j += 2
                else:
                    if flatten_straight:
                        points = Segment(prev, curr).flatten(custom_len, distance)
                        for k in range(1, len(points)):
                            new_contour.append(points[k])
                    else:
                        new_contour.append(curr)
                j += 1
            new_path.append(new_contour)

        self.path = new_path

    def move(self, x: float = 0, y: float = 0) -> None:
        """Moves the path by specified distance."""
        self.map(lambda px, py, point: point.move(x, y))

    def rotate(self, angle: float, c: Point | None = None) -> None:
        """Rotates the path by specified angle."""
        if c is None:
            c = self.bounding_box["center"]
        self.map(lambda px, py, point: point.rotate(angle, c))

    def rotate_frz(self, angle: float) -> None:
        """Rotates the path by specified angle."""
        self.map(lambda px, py, point: point.rotate_frz(angle))

    def scale(self, hor: float = 100, ver: float = 100) -> None:
        """Scales the path by specified horizontal and vertical values."""
        self.map(lambda px, py, point: point.scale(hor, ver))

    def to_origin(self) -> None:
        """Moves the points to the origin of the plane."""
        origin = self.bounding_box["origin"]
        self.move(-origin.x, -origin.y)

    def to_center(self) -> None:
        """Moves the points to the center of the plane."""
        center = self.bounding_box["center"]
        self.move(-center.x, -center.y)

    def reallocate(self, an: int, box: BoundingBoxType | None = None, rev: bool = False, x: float = 0, y: float = 0):
        """Reallocates the shape to align 7 or from align 7 to any other align."""
        if box is None:
            box = self.bounding_box
        width = box["width"]
        height = box["height"]
        match an:
            case 1 | 4 | 7:
                tx = 0
            case 2 | 5 | 8:
                tx = 0.5
            case 3 | 6 | 9:
                tx = 1
            case _:
                raise ValueError("an should be an integer between 1 and 9")
        match an:
            case 7 | 8 | 9:
                ty = 0
            case 4 | 5 | 6:
                ty = 0.5
            case 1 | 2 | 3:
                ty = 1
            case _:
                raise ValueError("an should be an integer between 1 and 9")
        if not rev:
            self.move(x - width * tx, y - height * ty)
        else:
            self.move(-x + width * tx, -y + height * ty)

    def perspective(self, mesh: list[float], real: list[Point] | None = None, mode: str = ""):
        """Makes a distortion based on the control points given by a quadrilateral."""

        def fn(_, __, point):
            uv = point.quad_PT2UV(*real)
            pt = uv.qual_UV2PT()
            return pt.x, pt.y

        path = self.create_rectangle(*mesh) if mode == "warping" else self
        if real is None:
            box = path.bounding_box
            l, t, r, b = box["l"], box["t"], box["r"], box["b"]
            real = [Point(l, t), Point(r, t), Point(r, b), Point(l, b)]
        self.map(fn)

    def envelope_grid(self, num_rows: int, num_cols: int, is_bezier: bool = False) -> tuple[Self, float, float]:
        """Creates a grid for the distortion envelope."""
        box = self.bounding_box
        l = box["l"]
        t = box["t"]
        width = box["width"]
        height = box["height"]
        row_distance = height / num_rows
        col_distance = width / num_cols
        rect = Shape()
        rect.path.append([
            Point(0, 0),
            Point(col_distance, 0),
            Point(col_distance, row_distance),
            Point(0, row_distance),
        ])
        rects_col = Shape()
        rects_row = Shape()
        for col in range(num_cols):
            new_rect = rect.copy()
            new_rect.move(col * col_distance, 0)
            rects_col.path.append(new_rect.path[1])
        for row in range(num_rows):
            new_rect = rect.copy()
            new_rect.move(0, row * row_distance)
            rects_row.path.extend(new_rect.path)
        if is_bezier:
            rects_row.close_contours()
            rects_row.all_curve()
        return rects_row.move(l, t), col_distance, row_distance

    def are_contours_open(self) -> bool:
        """Checks if all contours are open."""
        return not any(contour[0] == contour[-1] for contour in self.path)

    def close_contours(self):
        for contour in self.path:
            first_point = contour[0]
            last_point = contour[-1]
            if first_point != last_point:
                new_point = first_point.copy()
                new_point.id = "l"
                contour.append(new_point)

    def open_contours(self):
        for contour in self.path:
            first_point = contour[0]
            last_point = contour[-1]
            if last_point.id == "l" and first_point == last_point:
                contour.pop()

    def clean_contours(self):
        i = 0
        while i < len(self.path):
            contour = self.path[i]
            j = 1
            while j < len(contour):
                prev = contour[j - 1]
                curr = contour[j]
                if curr.id == "b":
                    if j > 2 and prev == curr:
                        j -= 1
                        contour.pop(j)
                    j += 2
                elif prev == curr:
                    contour.pop(j)
                j += 1
            if len(contour) < 3:
                self.path.pop(i)
            else:
                i += 1

    def all_curve(self):
        new_path = []
        for contour in self.path:
            j = 1
            add = [contour[0].copy()]
            while j < len(contour):
                prev = contour[j - 1]
                curr = contour[j]
                if curr.id == "b":
                    add.append(curr)
                    add.append(contour[j + 1])
                    add.append(contour[j + 2])
                    j += 2
                else:
                    if prev != curr:
                        a, b, c, d = Segment(prev, curr).line_to_bezier()
                        add.append(b)
                        add.append(c)
                        add.append(d)
                    else:
                        add.append(curr)
                j += 1
            new_path.append(add)
        self.path = new_path

    def get_length(self):
        def fn(_, seg, __):
            nonlocal length
            length += seg.get_length()

        length = 0
        self.callback_path(fn)
        return length

    def get_normalized(self, t: float = 0.5) -> tuple[Point, Point, float, Self]:
        def fn(_, seg, k):
            nonlocal sum_length, tan, p, u
            segment_len = seg.get_length()
            if k > len(new_path.path):
                new_path.path.append([seg.a])
            if sum_length + segment_len >= length:
                u = (length - sum_length) / segment_len
                tan, p, u = seg.get_normalized(u)
                spt = seg.split(u)[0]
                if id == "l":
                    new_path.path[k].append(spt.b)
                elif id == "b":
                    new_path.path[k].append(spt.b)
                    new_path.path[k].append(spt.c)
                    new_path.path[k].append(spt.d)
                return "break"
            if id == 'l':
                new_path.path[k].append(seg.b)
            else:
                new_path.path[k].append(seg.b)
                new_path.path[k].append(seg.c)
                new_path.path[k].append(seg.d)
            sum_length += segment_len
            return None

        sum_length = 0
        length = t * self.get_length()
        new_path = Shape()
        tan, p, u = None, None, None
        self.callback_path(fn)
        return tan, p, u, new_path

    def in_clip(self, an: int = 7, clip: str | Self | None = None,
                mode: Literal[1, 2, 3, "left", "center", "right"] | int | str = "center", len_: float | None = None,
                offset: float = 0) -> None:
        """Distorts the shape into another shape."""
        box = self.bounding_box
        origin, width, height = box["origin"], box["width"], box["height"]
        ox, oy = origin.x, origin.y
        clip = Shape(clip)
        clip.open_contours()
        if len_ is None:
            len_ = clip.get_length()
        size = len_ - width
        self.flatten(flatten_straight=True)
        match mode:
            case 1 | "left":
                sx = -ox + offset
            case 2 | "center":
                sx = -ox + offset + size / 2
            case 3 | "right":
                sx = -ox + offset + size
            case _:
                raise TypeError(f"Invalid mode: {mode}")
        match an:
            case 7 | 8 | 9:
                sy = -oy - height
            case 4 | 5 | 6:
                sy = -oy - height / 2
            case 1 | 2 | 3:
                sy = -oy
            case _:
                raise TypeError(f"Invalid an: {an}")

        def fn(px, py, point):
            nonlocal len_
            tan, pnt, *_ = clip.get_normalized((sx + px) / len_)
            point.x = pnt.x + (sy + py) * tan.x
            point.y = pnt.y + (sy + py) * tan.y

        self.map(fn)
