from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "AssColor",
]


@dataclass(slots=True)
class AssColor:
    r: int
    g: int
    b: int

    @classmethod
    def from_ass(cls, raw: str) -> AssColor:
        from ..utils.type_parser import TypeParser

        return TypeParser.parse_color(raw)

    @classmethod
    def from_hex(cls, raw: str) -> AssColor:
        r = int(raw[0:2], 16)
        g = int(raw[2:4], 16)
        b = int(raw[4:6], 16)
        return cls(r, g, b)

    @classmethod
    def parse(cls, s: str) -> AssColor:
        if s.startswith("#"):
            return cls.from_hex(s)
        return cls.from_ass(s)

    def format(self, template: str = "&H{B}{G}{R}") -> str:
        template = template.upper()
        return template.format(
            B="%02X" % self.b,
            G="%02X" % self.g,
            R="%02X" % self.r,
        )

    def to_ass(self) -> str:
        return self.format()

    def __str__(self) -> str:
        return self.to_ass()
