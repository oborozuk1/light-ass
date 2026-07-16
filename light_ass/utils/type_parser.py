from __future__ import annotations

import re
from typing import TypeVar

from ..types import Align, AssAlpha, AssColor

INT32_MIN = -2_147_483_648
INT32_MAX = 2_147_483_647

VT = TypeVar("VT", bound=int | float)


def clamp(val: VT, min_: VT, max_: VT) -> VT:
    return min(max(val, min_), max_)


class TypeParser:
    FLOAT_STR_REGEX = re.compile(r"\s*[+-]?\d*\.?\d*(?:[eE][+-]?\d+)?", flags=re.ASCII)
    INT_STR_REGEX = re.compile(r"\s*[+-]?\d*", flags=re.ASCII)
    HEX_STR_REGEX = re.compile(r"\s*[+-]?[\da-f]*", flags=re.ASCII)

    @staticmethod
    def parse_int_with_pos(param: str, strict: bool = False, pos: int = 0) -> tuple[int, int]:
        match = TypeParser.INT_STR_REGEX.match(param, pos)
        if not match or not match.group(0):
            raise ValueError(f"Invalid integer value: {param[pos:]!r}")
        try:
            return int(match.group(0)), match.end(0)
        except ValueError as e:
            if strict:
                raise e
            return 0, len(param)

    @staticmethod
    def parse_int(param: str, strict: bool = False) -> int:
        return TypeParser.parse_int_with_pos(param, strict)[0]

    @staticmethod
    def parse_align(param: str, strict: bool = False) -> Align:
        return Align(TypeParser.parse_int(param, strict))

    @staticmethod
    def parse_bool(param: str, strict: bool = False) -> bool:
        param = param.lstrip(" \t")
        if not param:
            raise ValueError(f"Invalid boolean value: {param!r}")
        val = TypeParser.parse_int(param, strict)
        if val == 0 or val == 1:
            return bool(val)
        raise ValueError(f"Invalid boolean value: {param!r}")

    @staticmethod
    def parse_float_with_pos(param: str, strict: bool = False, pos: int = 0) -> tuple[float, int]:
        match = TypeParser.FLOAT_STR_REGEX.match(param, pos)
        if not match or not match.group(0):
            raise ValueError(f"Invalid float value: {param[pos:]!r}")
        try:
            return float(match.group(0)), match.end(0)
        except ValueError as e:
            if strict:
                raise e
            return 0.0, len(param)

    @staticmethod
    def parse_float(param: str, strict: bool = False) -> float:
        return TypeParser.parse_float_with_pos(param, strict)[0]

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
