from __future__ import annotations

from typing import TYPE_CHECKING, Self

from ...types.align import Align
from ...utils import TypeParser
from .base import EffectGroup, FirstPolicy, RawTag, SimpleTag, Tag

if TYPE_CHECKING:
    from ..parser import TagParser


class AlignmentTag(SimpleTag[Align]):
    __slots__ = ("_value",)

    tag_name = "an"
    effect_group = EffectGroup("alignment", FirstPolicy)
    _parse_param = staticmethod(TypeParser.parse_align)
    _value: Align | None

    def __init__(self, value: Align | int | None = None, _raw: RawTag | None = None) -> None:
        Tag.__init__(self, _raw=_raw)
        if isinstance(value, int):
            value = Align(value)
        self._value = value
        self._dirty = False

    @property
    def value(self) -> Align | None:
        return self._value

    @value.setter
    def value(self, value: Align | int | None) -> None:
        if isinstance(value, int):
            self._value = Align(value)
        else:
            self._value = value

    def get_params(self) -> tuple[Align | None]:
        return (self._value,)


class LegacyAlignmentTag(SimpleTag[Align]):
    __slots__ = ("_value",)

    tag_name = "a"
    effect_group = EffectGroup("alignment", FirstPolicy)

    @staticmethod
    def _parse_param(param: str) -> Align:
        return Align.from_legacy(TypeParser.parse_int(param))

    _value: Align | None

    def __init__(self, value: Align | int | None = None, _raw: RawTag | None = None) -> None:
        Tag.__init__(self, _raw=_raw)
        if isinstance(value, int):
            value = Align(value)
        self._value = value
        self._dirty = False

    @property
    def value(self) -> Align | None:
        return self._value

    @value.setter
    def value(self, value: Align | int | None) -> None:
        if isinstance(value, int):
            self._value = Align.from_legacy(value)
        else:
            self._value = value

    def get_params(self) -> tuple[Align | None]:
        return (self._value,)
