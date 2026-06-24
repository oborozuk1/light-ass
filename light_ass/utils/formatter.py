from __future__ import annotations

from typing import Any

from ..types import AssAlpha, AssColor


class Formatter:
    decimal = 10

    @staticmethod
    def format_float(number: float, decimal: int | None = None) -> str:
        if decimal is None:
            decimal = Formatter.decimal
        if decimal <= 0:
            scale = 10**-decimal
            val = round(number / scale) * scale
            return str(int(val))
        return f"{number:.{decimal}f}".rstrip("0").rstrip(".")

    @staticmethod
    def format(value: Any, decimal: int | None = None) -> str:
        match value:
            case float():
                if decimal is None:
                    decimal = Formatter.decimal
                return Formatter.format_float(value, decimal)
            case bool():
                return "1" if value else "0"
            case AssColor():
                return value.to_ass()
            case AssAlpha():
                return value.to_ass()
            case _:
                return str(value)
