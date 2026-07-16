from __future__ import annotations

from ..point import Point as _BasePoint


class Point(_BasePoint):
    __slots__ = ()

    def format(self, decimal: int | None = None, sep: str = " ") -> str:
        from ...utils import Formatter

        fmt = Formatter.format_float
        return f"{fmt(self.x, decimal)}{sep}{fmt(self.y, decimal)}"
