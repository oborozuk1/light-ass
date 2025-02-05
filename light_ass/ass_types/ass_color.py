from itertools import takewhile
from typing import overload, Self


class AssColor:
    @overload
    def __init__(self, color: str | Self): ...

    @overload
    def __init__(self, r: int, g: int, b: int, a: int | None = None):
        ...

    def __init__(
            self,
            color_or_r: int | str | Self,
            g: int | None = None,
            b: int | None = None,
            a: int | None = None,
    ):
        self.value = 0
        if isinstance(color_or_r, str):
            color = color_or_r.lstrip("&H").lstrip(" \t")
            color = "".join(takewhile(lambda x: x in "0123456789ABCDEF", color))
            value = int(color, 16)
            if value < 0 or value > 0xFFFFFFFF:
                raise ValueError("Invalid color value")
            r = value & 0xFF
            g = (value >> 8) & 0xFF
            b = (value >> 16) & 0xFF
            a = (value >> 24) & 0xFF
            value = (r << 24) | (g << 16) | (b << 8) | a
        elif isinstance(color_or_r, int) and g is not None and b is not None:
            if a is None:
                a = 0
            if not all(0 <= i <= 255 for i in (color_or_r, g, b, a)):
                raise ValueError("r, g, b, a must be between 0 and 255")
            value = (color_or_r << 24) | (g << 16) | (b << 8) | a
        elif isinstance(color_or_r, AssColor):
            value = color_or_r.value
        else:
            raise TypeError("Unsupported type")
        self.value = value  # RGBA

    @property
    def r(self) -> int:
        return (self.value >> 24) & 0xFF

    @r.setter
    def r(self, value):
        self.value = (self.value & 0x00FFFFFF) | (value << 24)

    @property
    def g(self) -> int:
        return (self.value >> 16) & 0xFF

    @g.setter
    def g(self, value):
        self.value = (self.value & 0xFF00FFFF) | (value << 16)

    @property
    def b(self) -> int:
        return (self.value >> 8) & 0xFF

    @b.setter
    def b(self, value):
        self.value = (self.value & 0xFFFF00FF) | (value << 8)

    @property
    def a(self) -> int:
        return self.value & 0xFF

    @a.setter
    def a(self, value):
        self.value = (self.value & 0xFFFFFF00) | value

    def __str__(self):
        return self.format("&H{A}{B}{G}{R}")

    def __eq__(self, other: str | Self):
        try:
            other = AssColor(other)
            return str(self) == str(other)
        except ValueError:
            return False

    def format(self, template: str | None = None) -> str:
        """
        Format the color into a template string.
        :param template: The template string, default is "&H{A}{B}{G}{R}" if alpha is present, "&H{B}{G}{R}" otherwise.
        :return: The formatted color string.
        """
        if template is None:
            template = "&H{A}{B}{G}{R}" if self.a else "&H{B}{G}{R}"
        template = template.upper()
        return template.format(
            A="%02X" % self.a,
            B="%02X" % self.b,
            G="%02X" % self.g,
            R="%02X" % self.r,
        )
