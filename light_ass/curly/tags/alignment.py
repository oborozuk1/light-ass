from __future__ import annotations

from ...types.align import Align
from ...utils import TypeParser
from .base import EffectGroup, FirstPolicy, SimpleTag


class AlignmentTag(SimpleTag[Align]):
    __slots__ = ()

    tag_name = "an"
    effect_group = EffectGroup("alignment", FirstPolicy)
    _parse_param = staticmethod(TypeParser.parse_align)

    @property
    def value(self) -> Align | None:
        return self._load_value()

    @value.setter
    def value(self, value: Align | int | None) -> None:
        if isinstance(value, int) and not isinstance(value, Align):
            value = Align(value)
        object.__setattr__(self, "_value", value)


class LegacyAlignmentTag(SimpleTag[Align]):
    __slots__ = ()

    tag_name = "a"
    effect_group = EffectGroup("alignment", FirstPolicy)

    @staticmethod
    def _parse_param(param: str) -> Align:
        return Align.from_legacy(TypeParser.parse_int(param))

    @property
    def value(self) -> Align | None:
        return self._load_value()

    @value.setter
    def value(self, value: Align | int | None) -> None:
        if isinstance(value, int) and not isinstance(value, Align):
            value = Align.from_legacy(value)
        object.__setattr__(self, "_value", value)
