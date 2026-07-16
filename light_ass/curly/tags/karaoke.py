from __future__ import annotations

from ...utils import TypeParser
from .base import SimpleTag


class KaraokeTag(SimpleTag[float]):
    __slots__ = ()

    tag_name = "k"
    _parse_param = staticmethod(TypeParser.parse_float)


class KaraokeSweepTag(SimpleTag[float]):
    __slots__ = ()

    tag_name = "kf"
    aliases = ("K",)
    _parse_param = staticmethod(TypeParser.parse_float)


class KaraokeOutlineTag(SimpleTag[float]):
    __slots__ = ()

    tag_name = "ko"
    _parse_param = staticmethod(TypeParser.parse_float)


class KaraokeTimeTag(SimpleTag[float]):
    __slots__ = ()

    tag_name = "kt"
    _parse_param = staticmethod(TypeParser.parse_float)
