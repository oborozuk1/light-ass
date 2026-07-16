from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Self

from ...utils import TypeParser
from .base import AccumulatePolicy, EffectGroup, RawTag, SimpleTag

if TYPE_CHECKING:
    from ..parser import TagParser


class FontSizeTag(SimpleTag[float], ABC):
    __slots__ = ()

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
            return tag_cls(TypeParser.parse_float(param), _raw=raw)
        except ValueError:
            return tag_cls(None, _raw=raw)


class FontSizeAbsoluteTag(FontSizeTag):
    __slots__ = ()

    def normalize(self) -> None:
        if self.value is not None and self.value < 0:
            self.value = None


class FontSizeRelativeTag(FontSizeTag):
    __slots__ = ()

    effect_group = EffectGroup("fontsize-relative", AccumulatePolicy)


class FontNameTag(SimpleTag[str]):
    __slots__ = ()

    tag_name = "fn"

    @staticmethod
    def _parse_param(param: str) -> str:
        return param

    @classmethod
    def from_raw(cls, raw: RawTag, strict: bool = False, parser: TagParser | None = None) -> Self:
        if len(raw.params) == 0:
            return cls(None, _raw=raw)

        if len(raw.params) > 1 and strict:
            raise ValueError(f"{cls.__name__} expected 1 param, got {len(raw.params)}")

        param = raw.params[0]
        if param == "0":
            return cls(None, _raw=raw)

        try:
            return cls(cls._parse_param(param), _raw=raw)
        except ValueError:
            return cls(None, _raw=raw)

    def normalize(self) -> None:
        if self.value == "0":
            self.value = None
        elif self.value is not None:
            self.value = self.value.strip(" \t")


class FontEncodingTag(SimpleTag[int]):
    __slots__ = ()

    tag_name = "fe"
    _parse_param = staticmethod(TypeParser.parse_int)


class LetterSpacingTag(SimpleTag[float]):
    __slots__ = ()

    tag_name = "fsp"
    _parse_param = staticmethod(TypeParser.parse_float)
