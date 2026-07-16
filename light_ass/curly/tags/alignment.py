from __future__ import annotations

from ...types.align import Align
from ...utils import TypeParser
from .base import EffectGroup, FirstPolicy, RawTag, SimpleTag


class AlignmentTag(SimpleTag[Align]):
    tag_name = "an"
    effect_group = EffectGroup("alignment", FirstPolicy)
    _parse_param = staticmethod(TypeParser.parse_align)
    _value: Align | None = None

    def __init__(self, value: Align | int | None = None, _raw: RawTag | None = None) -> None:
        self._raw = _raw
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

    def __repr__(self) -> str:
        return f"AlignmentTag(value={self._value})"


class LegacyAlignmentTag(SimpleTag[Align]):
    tag_name = "a"
    effect_group = EffectGroup("alignment", FirstPolicy)
    _parse_param = staticmethod(TypeParser.parse_align)
    _value: Align | None = None

    def __init__(self, value: Align | int | None = None, _raw: RawTag | None = None) -> None:
        self._raw = _raw
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

    def __repr__(self) -> str:
        return f"LegacyAlignmentTag(value={self._value})"
