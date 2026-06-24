from __future__ import annotations

import re
from typing import TypeVar

from ..types import AssAlpha, AssColor

INT32_MIN = -2_147_483_648
INT32_MAX = 2_147_483_647

VT = TypeVar("VT", bound=int | float)


def clamp(val: VT, min_: VT, max_: VT) -> VT:
    return min(max(val, min_), max_)


class TypeParser:
    FLOAT_STR_REGEX = re.compile(r"^\s*[+-]?\d*\.?\d*(?:[eE][+-]?\d+)?", flags=re.ASCII)
    INT_STR_REGEX = re.compile(r"^\s*[+-]?\d*", flags=re.ASCII)
    HEX_STR_REGEX = re.compile(r"^\s*[+-]?[\da-f]*", flags=re.ASCII)

    @staticmethod
    def parse_int(param: str) -> int:
        match = TypeParser.INT_STR_REGEX.match(param)
        if not match or not match.group(0):
            raise ValueError(f"Invalid integer value: {param!r}")
        try:
            return int(match.group(0))
        except ValueError:
            return 0

    @staticmethod
    def parse_bool(param: str) -> bool:
        param = param.lstrip(" \t")
        if not param:
            raise ValueError(f"Invalid boolean value: {param!r}")
        val = TypeParser.parse_int(param)
        if val == 0 or val == 1:
            return bool(val)
        raise ValueError(f"Invalid boolean value: {param!r}")

    @staticmethod
    def parse_float(param: str) -> float:
        match = TypeParser.FLOAT_STR_REGEX.match(param)
        if not match or not match.group(0):
            raise ValueError(f"Invalid float value: {param!r}")
        try:
            return float(match.group(0))
        except ValueError:
            return 0.0

    @staticmethod
    def parse_str(param: str) -> str:
        return param.lstrip(" \t")

    @staticmethod
    def int_to_int32(val: int) -> int:
        return clamp(val, INT32_MIN, INT32_MAX)

    @staticmethod
    def hex_to_int(text: str) -> int:
        match = TypeParser.HEX_STR_REGEX.match(text)
        if not match or not match.group(0):
            raise ValueError(f"Invalid hex value: {text!r}")
        try:
            return int(match.group(0), 16)
        except ValueError:
            return 0

    @staticmethod
    def parse_color(param: str) -> AssColor:
        param = param.lstrip(" \t").lower().lstrip("&h")
        hex_value = TypeParser.int_to_int32(TypeParser.hex_to_int(param))
        r = hex_value & 255
        g = (hex_value >> 8) & 255
        b = (hex_value >> 16) & 255
        return AssColor(r, g, b)

    @staticmethod
    def parse_alpha(param: str) -> AssAlpha:
        param = param.lstrip(" \t").lower().lstrip("&h")
        hex_value = TypeParser.int_to_int32(TypeParser.hex_to_int(param)) & 0xFF
        return AssAlpha(hex_value)
