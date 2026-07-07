from __future__ import annotations

from ..constants import YCbCrMatrix
from ..types import AssAlpha, AssColor, AssTime
from .type_parser import TypeParser


class HeaderTypeParser:
    @staticmethod
    def parse_str(s: str) -> str:
        return s.lstrip(" \t")

    @staticmethod
    def parse_starred_str(s: str) -> str:
        return s.lstrip(" \t").lstrip("*")

    @staticmethod
    def parse_bool(s: str) -> bool:
        s = s.lstrip(" \t").lower()
        if s == "yes":
            return True
        try:
            return TypeParser.parse_int(s) > 0
        except ValueError:
            return False

    @staticmethod
    def parse_int_bool(s: str) -> bool:
        s = s.lstrip(" \t").lower()
        try:
            num = TypeParser.parse_int(s)
            return num == -1
        except ValueError:
            return False

    @staticmethod
    def _parse_int(s: str, base: int = 10) -> int:
        if base == 10:
            match = TypeParser.INT_STR_REGEX.match(s)
            if not match or not match.group(0):
                return 0
            return int(match.group(0))
        elif base == 16:
            match = TypeParser.HEX_STR_REGEX.match(s.lower())
            if not match or not match.group(0):
                return 0
            return int(match.group(0), 16)
        return int(s, base)

    @staticmethod
    def parse_int(s: str) -> int:
        s = s.lower()
        base = 10
        if s.startswith(("&h", "0x")):
            s = s[2:]
            base = 16
        try:
            return HeaderTypeParser._parse_int(s, base)
        except ValueError:
            return 0

    @staticmethod
    def parse_float(s: str) -> float:
        return TypeParser.parse_float(s)

    @staticmethod
    def parse_ycbcr_matrix(s: str) -> YCbCrMatrix | str:
        s = s.lstrip(" \t").upper()
        for member in YCbCrMatrix:
            if s.startswith(member.value):
                return member
        return s

    @staticmethod
    def parse_color_with_alpha(param: str) -> tuple[AssColor, AssAlpha]:
        param = param.lstrip(" \t").lower().lstrip("&h")
        hex_value = TypeParser.hex_to_int(param)
        r = hex_value & 255
        g = (hex_value >> 8) & 255
        b = (hex_value >> 16) & 255
        a = (hex_value >> 24) & 255
        return AssColor(r, g, b), AssAlpha(a)

    @staticmethod
    def parse_time(s: str) -> AssTime:
        return AssTime.parse(s)
