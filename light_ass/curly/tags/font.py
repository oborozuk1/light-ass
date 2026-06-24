from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import TYPE_CHECKING

from ...utils import TypeParser
from .base import RawTag, SimpleTag

if TYPE_CHECKING:
    from ..parser import TagParser


@dataclass
class FontSizeTag(SimpleTag[float], ABC):
    tag_name = "fs"
    _parse_param = staticmethod(TypeParser.parse_float)

    @classmethod
    def from_raw(
        cls, raw: RawTag, strict: bool = False, parser: TagParser | None = None
    ) -> FontSizeAbsoluteTag | FontSizeRelativeTag:
        if len(raw.params) == 0:
            return FontSizeAbsoluteTag(None, _raw=raw)

        if len(raw.params) > 1 and strict:
            raise ValueError(f"{cls.__name__} expected 1 param, got {len(raw.params)}")

        param = raw.params[0]

        tag_cls: type[FontSizeAbsoluteTag] | type[FontSizeRelativeTag] = FontSizeAbsoluteTag
        if param[0] in "+-":
            tag_cls = FontSizeRelativeTag

        try:
            return tag_cls(TypeParser.parse_float(param))
        except ValueError:
            return tag_cls(None, _raw=raw)


@dataclass
class FontSizeAbsoluteTag(FontSizeTag):
    value: float | None


@dataclass
class FontSizeRelativeTag(FontSizeTag):
    value: float | None


@dataclass
class FontNameTag(SimpleTag[str]):
    tag_name = "fn"
    _parse_param = staticmethod(TypeParser.parse_str)
    value: str | None


@dataclass
class FontEncodingTag(SimpleTag[int]):
    tag_name = "fe"
    _parse_param = staticmethod(TypeParser.parse_int)
    value: int | None


@dataclass
class LetterSpacingTag(SimpleTag[float]):
    tag_name = "fsp"
    _parse_param = staticmethod(TypeParser.parse_float)
    value: float | None
