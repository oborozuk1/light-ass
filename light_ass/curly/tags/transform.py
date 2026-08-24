from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING, Any, cast

from ...utils import TypeParser
from .base import _UNSET, AccumulatePolicy, EffectGroup, ParensTag, RawTag

if TYPE_CHECKING:
    from ..override_block import OverrideBlock
    from ..parser import TagParser
    from .base import _Unset


def _parse_timing(params: tuple[str, ...]) -> tuple[int | None, int | None, float | None]:
    length = len(params)
    if length == 2:
        return None, None, TypeParser.parse_float(params[0])
    if length == 3:
        return TypeParser.parse_int(params[0]), TypeParser.parse_int(params[1]), None
    if length == 4:
        return (
            TypeParser.parse_int(params[0]),
            TypeParser.parse_int(params[1]),
            TypeParser.parse_float(params[2]),
        )
    return None, None, None


class TransformTag(ParensTag):
    __slots__ = ("_modifier", "_modifier_raw", "_parser", "_strict", "t1", "t2", "accel")

    tag_name = "t"
    effect_group = EffectGroup("transform", AccumulatePolicy)

    _modifier: OverrideBlock | _Unset
    _modifier_raw: str | None
    _parser: TagParser | None
    _strict: bool
    t1: int | None
    t2: int | None
    accel: float | None

    def __init__(
        self,
        modifier: OverrideBlock,
        t1: int | None = None,
        t2: int | None = None,
        accel: float | None = None,
        _raw: RawTag | None = None,
    ) -> None:
        super().__init__(_raw=_raw)
        object.__setattr__(self, "_modifier_raw", None)
        object.__setattr__(self, "_parser", None)
        object.__setattr__(self, "_strict", False)
        object.__setattr__(self, "modifier", modifier)
        object.__setattr__(self, "t1", t1)
        object.__setattr__(self, "t2", t2)
        object.__setattr__(self, "accel", accel)

    @property
    def modifier(self) -> OverrideBlock:
        modifier = self._modifier
        if modifier is _UNSET:
            parser = self._parser
            modifier_raw = self._modifier_raw
            if parser is None or modifier_raw is None:
                raise ValueError("TagParser is required to parse the modifier of TransformTag")
            modifier = parser.parse_modifier(modifier_raw, strict=self._strict)
            object.__setattr__(self, "_modifier", modifier)
            object.__setattr__(self, "_modifier_raw", None)
            object.__setattr__(self, "_parser", None)
        return cast("OverrideBlock", modifier)

    @modifier.setter
    def modifier(self, modifier: OverrideBlock) -> None:
        object.__setattr__(self, "_modifier", modifier)
        object.__setattr__(self, "_modifier_raw", None)
        object.__setattr__(self, "_parser", None)

    @classmethod
    def from_raw(
        cls, raw: RawTag, strict: bool = False, parser: TagParser | None = None
    ) -> TransformTag:
        length = len(raw.params)
        if length not in (1, 2, 3, 4):
            raise ValueError(f"{cls.__name__} expected 1, 2, 3 or 4 params, got {length}")

        if parser is None:
            raise ValueError("TagParser is required to parse the modifier of TransformTag")

        if strict:
            modifier = parser.parse_modifier(raw.params[-1], strict=True)
            t1, t2, accel = _parse_timing(raw.params)
            return cls(modifier, t1, t2, accel, _raw=raw)

        t1, t2, accel = _parse_timing(raw.params)
        tag = cls.__new__(cls)
        object.__setattr__(tag, "_raw", raw)
        object.__setattr__(tag, "_dirty", False)
        object.__setattr__(tag, "_modifier", _UNSET)
        object.__setattr__(tag, "_modifier_raw", raw.params[-1])
        object.__setattr__(tag, "_parser", parser)
        object.__setattr__(tag, "_strict", False)
        object.__setattr__(tag, "t1", t1)
        object.__setattr__(tag, "t2", t2)
        object.__setattr__(tag, "accel", accel)
        return tag

    def __deepcopy__(self, memo: dict[int, Any]) -> TransformTag:
        cls = self.__class__
        new = cls.__new__(cls)
        memo[id(self)] = new
        object.__setattr__(new, "_raw", self._raw)
        object.__setattr__(new, "_dirty", self._dirty)
        object.__setattr__(new, "t1", self.t1)
        object.__setattr__(new, "t2", self.t2)
        object.__setattr__(new, "accel", self.accel)
        object.__setattr__(new, "_parser", self._parser)
        object.__setattr__(new, "_strict", self._strict)
        modifier = self._modifier
        if modifier is _UNSET:
            object.__setattr__(new, "_modifier", _UNSET)
            object.__setattr__(new, "_modifier_raw", self._modifier_raw)
        else:
            object.__setattr__(new, "_modifier", deepcopy(modifier, memo))
            object.__setattr__(new, "_modifier_raw", None)
        return new

    def get_params(self) -> dict[str, OverrideBlock | int | float]:
        params: dict[str, OverrideBlock | int | float] = {}
        if self.t1 is not None and self.t2 is not None:
            params["t1"] = self.t1
            params["t2"] = self.t2
        if self.accel is not None:
            params["accel"] = self.accel
        params["modifier"] = self.modifier
        return params

    def to_ass(self) -> str:
        return self._serialize()
