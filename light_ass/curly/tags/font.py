from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

from ...utils import TypeParser
from .base import RawTag, SimpleTag, EffectGroup, AccumulatePolicy

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

    def normalize(self) -> None:
        if self.value is not None and self.value < 0:
            self.value = None


@dataclass
class FontSizeRelativeTag(FontSizeTag):
    value: float | None
    effect_group = EffectGroup("fontsize-relative", AccumulatePolicy)


@dataclass
class FontNameTag(SimpleTag[str]):
    tag_name = "fn"
    value: str | None

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
