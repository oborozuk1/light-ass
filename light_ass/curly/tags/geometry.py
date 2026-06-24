from __future__ import annotations

from dataclasses import dataclass

from ...utils import TypeParser
from .base import SimpleTag


@dataclass
class ScaleXTag(SimpleTag[float]):
    tag_name = "fscx"
    _parse_param = staticmethod(TypeParser.parse_float)
    value: float | None


@dataclass
class ScaleYTag(SimpleTag[float]):
    tag_name = "fscy"
    _parse_param = staticmethod(TypeParser.parse_float)
    value: float | None


@dataclass
class ScaleTag(SimpleTag[None]):
    tag_name = "fsc"

    @staticmethod
    def _parse_param(param: str) -> None:
        raise ValueError(f"{ScaleTag.__name__} does not accept parameters")

    def _serialize(self) -> str:
        return "\\fsc"


@dataclass
class RotateXTag(SimpleTag[float]):
    tag_name = "frx"
    _parse_param = staticmethod(TypeParser.parse_float)
    value: float | None


@dataclass
class RotateYTag(SimpleTag[float]):
    tag_name = "fry"
    _parse_param = staticmethod(TypeParser.parse_float)
    value: float | None


@dataclass
class RotateZTag(SimpleTag[float]):
    tag_name = "frz"
    aliases = ("fr",)
    _parse_param = staticmethod(TypeParser.parse_float)
    value: float | None


@dataclass
class ShearXTag(SimpleTag[float]):
    tag_name = "fax"
    _parse_param = staticmethod(TypeParser.parse_float)
    value: float | None


@dataclass
class ShearYTag(SimpleTag[float]):
    tag_name = "fay"
    _parse_param = staticmethod(TypeParser.parse_float)
    value: float | None


@dataclass
class DrawingModeTag(SimpleTag[int]):
    tag_name = "p"
    _parse_param = staticmethod(TypeParser.parse_int)
    value: int | None


@dataclass
class DrawingBaselineOffsetTag(SimpleTag[float]):
    tag_name = "pbo"
    _parse_param = staticmethod(TypeParser.parse_float)
    value: float | None
