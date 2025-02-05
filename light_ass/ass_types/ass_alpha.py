from itertools import takewhile
from typing import Self


class AssAlpha:
    def __init__(self, val: str | int | Self):
        if isinstance(val, str) or isinstance(val, int):
            self.value = self.parse(val)
        elif isinstance(val, AssAlpha):
            self.value = val.value
        else:
            raise ValueError("Unsupported type")

    @property
    def hex_value(self) -> str:
        """
        Get the alpha value as a hex string.
        :return: The alpha value as a hex string.
        """
        from ..utils import clamp

        val = clamp(self.value, 0, 255)
        return f"{val:02x}"

    @staticmethod
    def parse(s: str | int) -> int:
        """
        Parse a string or integer to an alpha value.
        :param s: The string or integer to parse.
        :return: The alpha value.
        """
        if isinstance(s, int):
            if 0 <= s <= 255:
                return s
            raise ValueError("Invalid alpha value")

        s = s.lstrip("&H").lstrip(" \t")
        s = "".join(takewhile(lambda x: x in "0123456789ABCDEF", s))
        val = int(s, 16)
        if 0 <= val <= 255:
            return val
        raise ValueError("Invalid alpha value")

    def format(self, template: str = "&H{A}&") -> str:
        """
        Format the alpha value into the template string.
        :param template: The template string. "{A}" represents the alpha value.
        :return: The formatted string.
        """
        return template.format(A=self.hex_value)

    def __eq__(self, other: str | int | Self):
        try:
            other = AssAlpha(other)
            return self.value == other.value
        except ValueError:
            return False

    def __int__(self):
        return self.value

    def __str__(self):
        return self.format()

    def __repr__(self):
        return f"AssAlpha({self.value})"
