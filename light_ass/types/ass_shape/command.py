from abc import ABC, abstractmethod

from .point import Point


def format_points(points: list[Point], decimal: int | None = None) -> str:
    return " ".join(p.format(decimal) for p in points)


class BaseDrawCmd(ABC):
    @abstractmethod
    def serialize(self, decimal: int | None = None) -> str:
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.serialize()})"


class MoveCmd(BaseDrawCmd):
    def __init__(self, p: Point):
        self.point = p

    def serialize(self, decimal: int | None = None) -> str:
        return f"m {self.point.format(decimal)}"


class MoveNoClosingCmd(BaseDrawCmd):
    def __init__(self, p: Point):
        self.point = p

    def serialize(self, decimal: int | None = None) -> str:
        return f"n {self.point.format(decimal)}"

class LineCmd(BaseDrawCmd):
    def __init__(self, points: list[Point]):
        self.points = points

    def serialize(self, decimal: int | None = None) -> str:
        return f"l {format_points(self.points, decimal)}"


class BezierCmd(BaseDrawCmd):
    def __init__(self, points: list[Point]):
        self.points = points

    def serialize(self, decimal: int | None = None) -> str:
        return f"b {format_points(self.points, decimal)}"


class BSplineCmd(BaseDrawCmd):
    def __init__(self, points: list[Point]):
        self.points = points

    def serialize(self, decimal: int | None = None) -> str:
        return f"s {format_points(self.points, decimal)}"


class ExtendSplineCmd(BaseDrawCmd):
    def __init__(self, points: list[Point]):
        self.points = points

    def serialize(self, decimal: int | None = None) -> str:
        return f"p {format_points(self.points, decimal)}"


class CloseCmd(BaseDrawCmd):
    def serialize(self, decimal: int | None = None) -> str:
        return "c"
