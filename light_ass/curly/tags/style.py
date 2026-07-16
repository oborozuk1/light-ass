from __future__ import annotations

from typing import TYPE_CHECKING

from ...utils import TypeParser
from .base import RawTag, SimpleTag

if TYPE_CHECKING:
    from ..parser import TagParser


class BorderTag(SimpleTag[float]):
    __slots__ = ()

    tag_name = "bord"
    _parse_param = staticmethod(TypeParser.parse_float)

    def normalize(self) -> None:
        if self.value is not None:
            self.value = max(0.0, self.value)


class BorderXTag(SimpleTag[float]):
    __slots__ = ()

    tag_name = "xbord"
    _parse_param = staticmethod(TypeParser.parse_float)

    def normalize(self) -> None:
        if self.value is not None:
            self.value = max(0.0, self.value)


class BorderYTag(SimpleTag[float]):
    __slots__ = ()

    tag_name = "ybord"
    _parse_param = staticmethod(TypeParser.parse_float)

    def normalize(self) -> None:
        if self.value is not None:
            self.value = max(0.0, self.value)


class ShadowTag(SimpleTag[float]):
    __slots__ = ()

    tag_name = "shad"
    _parse_param = staticmethod(TypeParser.parse_float)

    def normalize(self) -> None:
        if self.value is not None:
            self.value = max(0.0, self.value)


class ShadowXTag(SimpleTag[float]):
    __slots__ = ()

    tag_name = "xshad"
    _parse_param = staticmethod(TypeParser.parse_float)


class ShadowYTag(SimpleTag[float]):
    __slots__ = ()

    tag_name = "yshad"
    _parse_param = staticmethod(TypeParser.parse_float)


class BlurEdgeTag(SimpleTag[float]):
    __slots__ = ()

    tag_name = "be"
    _parse_param = staticmethod(TypeParser.parse_float)

    def normalize(self) -> None:
        if self.value is not None:
            self.value = max(0.0, self.value)


class BlurTag(SimpleTag[float]):
    __slots__ = ()

    tag_name = "blur"
    _parse_param = staticmethod(TypeParser.parse_float)

    def normalize(self) -> None:
        if self.value is not None:
            self.value = max(0.0, self.value)


class BoldTag(SimpleTag[int]):
    __slots__ = ()

    tag_name = "b"
    _parse_param = staticmethod(TypeParser.parse_int)

    @classmethod
    def from_raw(
        cls, raw: RawTag, strict: bool = False, parser: TagParser | None = None
    ) -> BoldSimpleTag | BoldWeightTag:
        if len(raw.params) == 0:
            return BoldSimpleTag(None, _raw=raw)

        if len(raw.params) > 1 and strict:
            raise ValueError(f"{cls.__name__} expected 1 param, got {len(raw.params)}")

        value = cls._parse_param(raw.params[0])
        if value == 0 or value == 1:
            return BoldSimpleTag(bool(value), _raw=raw)
        return BoldWeightTag(value, _raw=raw)


class BoldSimpleTag(BoldTag, SimpleTag[bool]):
    __slots__ = ()


class BoldWeightTag(BoldTag, SimpleTag[int]):
    __slots__ = ()

    def normalize(self) -> None:
        if self.value is not None and self.value < 100:
            self.value = None


class ItalicTag(SimpleTag[bool]):
    __slots__ = ()

    tag_name = "i"
    _parse_param = staticmethod(TypeParser.parse_bool)


class UnderlineTag(SimpleTag[bool]):
    __slots__ = ()

    tag_name = "u"
    _parse_param = staticmethod(TypeParser.parse_bool)


class StrikeoutTag(SimpleTag[bool]):
    __slots__ = ()

    tag_name = "s"
    _parse_param = staticmethod(TypeParser.parse_bool)


class WrapStyleTag(SimpleTag[int]):
    __slots__ = ()

    tag_name = "q"
    _parse_param = staticmethod(TypeParser.parse_int)

    def normalize(self) -> None:
        if self.value is not None and not 1 <= self.value <= 3:
            self.value = None


class ResetStyleTag(SimpleTag[str]):
    __slots__ = ()

    tag_name = "r"
    _parse_param = staticmethod(TypeParser.parse_str)
