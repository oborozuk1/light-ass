from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "AssAlpha",
]


@dataclass(slots=True)
class AssAlpha:
    value: int

    @property
    def hex_value(self) -> str:
        return f"{self.value & 0xFF:02X}"

    @classmethod
    def parse(cls, s: str | int) -> AssAlpha:
        from ..utils.type_parser import TypeParser

        if isinstance(s, int):
            if 0 <= s <= 255:
                return cls(s)
            raise ValueError("Invalid alpha value")
        return TypeParser.parse_alpha(s)

    def format(self, template: str = "&H{A}&") -> str:
        return template.format(A=self.hex_value)

    def to_ass(self) -> str:
        return self.format()
