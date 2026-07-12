from collections.abc import Iterator
from dataclasses import dataclass


@dataclass(slots=True)
class Point:
    x: float
    y: float

    def __iter__(self) -> Iterator[float]:
        yield self.x
        yield self.y

    def format(self, decimal: int | None = None, sep: str = " ") -> str:
        from ...utils import Formatter

        fmt = Formatter.format_float
        return f"{fmt(self.x, decimal)}{sep}{fmt(self.y, decimal)}"

    def scale(self, factor_x: float, factor_y: float | None = None) -> None:
        if factor_y is None:
            factor_y = factor_x
        self.x *= factor_x
        self.y *= factor_y
