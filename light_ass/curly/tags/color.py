from __future__ import annotations

from dataclasses import dataclass

from ...types import AssAlpha, AssColor
from ...utils import TypeParser
from .base import SimpleTag


@dataclass
class AlphaTag(SimpleTag[AssAlpha]):
    tag_name = "alpha"
    _parse_param = staticmethod(TypeParser.parse_alpha)
    value: AssAlpha | None


@dataclass
class PrimaryAlphaTag(SimpleTag[AssAlpha]):
    tag_name = "1a"
    _parse_param = staticmethod(TypeParser.parse_alpha)
    value: AssAlpha | None


@dataclass
class SecondaryAlphaTag(SimpleTag[AssAlpha]):
    tag_name = "2a"
    _parse_param = staticmethod(TypeParser.parse_alpha)
    value: AssAlpha | None


@dataclass
class OutlineAlphaTag(SimpleTag[AssAlpha]):
    tag_name = "3a"
    _parse_param = staticmethod(TypeParser.parse_alpha)
    value: AssAlpha | None


@dataclass
class ShadowAlphaTag(SimpleTag[AssAlpha]):
    tag_name = "4a"
    _parse_param = staticmethod(TypeParser.parse_alpha)
    value: AssAlpha | None


@dataclass
class PrimaryColorTag(SimpleTag[AssColor]):
    tag_name = "1c"
    aliases = ("c",)
    _parse_param = staticmethod(TypeParser.parse_color)
    value: AssColor | None


@dataclass
class SecondaryColorTag(SimpleTag[AssColor]):
    tag_name = "2c"
    _parse_param = staticmethod(TypeParser.parse_color)
    value: AssColor | None


@dataclass
class OutlineColorTag(SimpleTag[AssColor]):
    tag_name = "3c"
    _parse_param = staticmethod(TypeParser.parse_color)
    value: AssColor | None


@dataclass
class ShadowColorTag(SimpleTag[AssColor]):
    tag_name = "4c"
    _parse_param = staticmethod(TypeParser.parse_color)
    value: AssColor | None
