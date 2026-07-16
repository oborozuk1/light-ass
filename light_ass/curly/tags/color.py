from __future__ import annotations

from ...types import AssAlpha, AssColor
from ...utils import TypeParser
from .base import SimpleTag


class AlphaTag(SimpleTag[AssAlpha]):
    __slots__ = ()

    tag_name = "alpha"
    _parse_param = staticmethod(TypeParser.parse_alpha)


class PrimaryAlphaTag(SimpleTag[AssAlpha]):
    __slots__ = ()

    tag_name = "1a"
    _parse_param = staticmethod(TypeParser.parse_alpha)


class SecondaryAlphaTag(SimpleTag[AssAlpha]):
    __slots__ = ()

    tag_name = "2a"
    _parse_param = staticmethod(TypeParser.parse_alpha)


class OutlineAlphaTag(SimpleTag[AssAlpha]):
    __slots__ = ()

    tag_name = "3a"
    _parse_param = staticmethod(TypeParser.parse_alpha)


class ShadowAlphaTag(SimpleTag[AssAlpha]):
    __slots__ = ()

    tag_name = "4a"
    _parse_param = staticmethod(TypeParser.parse_alpha)


class PrimaryColorTag(SimpleTag[AssColor]):
    __slots__ = ()

    tag_name = "1c"
    aliases = ("c",)
    _parse_param = staticmethod(TypeParser.parse_color)


class SecondaryColorTag(SimpleTag[AssColor]):
    __slots__ = ()

    tag_name = "2c"
    _parse_param = staticmethod(TypeParser.parse_color)


class OutlineColorTag(SimpleTag[AssColor]):
    __slots__ = ()

    tag_name = "3c"
    _parse_param = staticmethod(TypeParser.parse_color)


class ShadowColorTag(SimpleTag[AssColor]):
    __slots__ = ()

    tag_name = "4c"
    _parse_param = staticmethod(TypeParser.parse_color)
