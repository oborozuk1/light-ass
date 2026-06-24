from __future__ import annotations

from dataclasses import dataclass

from ...utils import TypeParser
from .base import SimpleTag


@dataclass
class KaraokeTag(SimpleTag[float]):
    tag_name = "k"
    _parse_param = staticmethod(TypeParser.parse_float)
    value: float | None


@dataclass
class KaraokeSweepTag(SimpleTag[float]):
    tag_name = "kf"
    aliases = ("K",)
    _parse_param = staticmethod(TypeParser.parse_float)
    value: float | None


@dataclass
class KaraokeOutlineTag(SimpleTag[float]):
    tag_name = "ko"
    _parse_param = staticmethod(TypeParser.parse_float)
    value: float | None


@dataclass
class KaraokeTimeTag(SimpleTag[float]):
    tag_name = "kt"
    _parse_param = staticmethod(TypeParser.parse_float)
    value: float | None
