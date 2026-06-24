from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ...utils import TypeParser
from .base import RawTag, SimpleTag

if TYPE_CHECKING:
    from ..parser import TagParser


@dataclass
class BorderTag(SimpleTag[float]):
    tag_name = "bord"
    _parse_param = staticmethod(TypeParser.parse_float)
    value: float | None


@dataclass
class BorderXTag(SimpleTag[float]):
    tag_name = "xbord"
    _parse_param = staticmethod(TypeParser.parse_float)
    value: float | None


@dataclass
class BorderYTag(SimpleTag[float]):
    tag_name = "ybord"
    _parse_param = staticmethod(TypeParser.parse_float)
    value: float | None


@dataclass
class ShadowTag(SimpleTag[float]):
    tag_name = "shad"
    _parse_param = staticmethod(TypeParser.parse_float)
    value: float | None


@dataclass
class ShadowXTag(SimpleTag[float]):
    tag_name = "xshad"
    _parse_param = staticmethod(TypeParser.parse_float)
    value: float | None


@dataclass
class ShadowYTag(SimpleTag[float]):
    tag_name = "yshad"
    _parse_param = staticmethod(TypeParser.parse_float)
    value: float | None


@dataclass
class BlurEdgeTag(SimpleTag[float]):
    tag_name = "be"
    _parse_param = staticmethod(TypeParser.parse_float)
    value: float | None


@dataclass
class BlurTag(SimpleTag[float]):
    tag_name = "blur"
    _parse_param = staticmethod(TypeParser.parse_float)
    value: float | None


@dataclass
class BoldTag(SimpleTag[int]):
    _parse_param = staticmethod(TypeParser.parse_int)
    tag_name = "b"

    @classmethod
    def from_raw(
        cls, raw: RawTag, strict: bool = False, parser: TagParser | None = None
    ) -> BoldSimpleTag | BoldWeightTag:
        if len(raw.params) == 0:
            return BoldSimpleTag(None)

        if len(raw.params) > 1 and strict:
            raise ValueError(f"{cls.__name__} expected 1 param, got {len(raw.params)}")

        value = cls._parse_param(raw.params[0])
        if value == 0 or value == 1:
            return BoldSimpleTag(bool(value))
        return BoldWeightTag(value)


@dataclass
class BoldSimpleTag(BoldTag, SimpleTag[bool]):
    value: bool | None


@dataclass
class BoldWeightTag(BoldTag, SimpleTag[int]):
    pass


@dataclass
class ItalicTag(SimpleTag[bool]):
    tag_name = "i"
    _parse_param = staticmethod(TypeParser.parse_bool)
    value: bool | None


@dataclass
class UnderlineTag(SimpleTag[bool]):
    tag_name = "u"
    _parse_param = staticmethod(TypeParser.parse_bool)
    value: bool | None


@dataclass
class StrikeoutTag(SimpleTag[bool]):
    tag_name = "s"
    _parse_param = staticmethod(TypeParser.parse_bool)
    value: bool | None


@dataclass
class WrapStyleTag(SimpleTag[int]):
    tag_name = "q"
    _parse_param = staticmethod(TypeParser.parse_int)
    value: int | None


@dataclass
class ResetStyleTag(SimpleTag[str]):
    tag_name = "r"
    _parse_param = staticmethod(TypeParser.parse_str)
    value: str | None
