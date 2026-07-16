from __future__ import annotations

from typing import TYPE_CHECKING

from ...utils import TypeParser
from .base import AccumulatePolicy, EffectGroup, ParensTag, RawTag

if TYPE_CHECKING:
    from ..override_block import OverrideBlock
    from ..parser import TagParser


class TransformTag(ParensTag):
    __slots__ = ("modifier", "t1", "t2", "accel")

    tag_name = "t"
    effect_group = EffectGroup("transform", AccumulatePolicy)

    def __init__(
        self,
        modifier: OverrideBlock,
        t1: int | None = None,
        t2: int | None = None,
        accel: float | None = None,
        _raw: RawTag | None = None,
    ) -> None:
        super().__init__(_raw=_raw)
        self.modifier = modifier
        self.t1 = t1
        self.t2 = t2
        self.accel = accel
        self._dirty = False

    @classmethod
    def from_raw(
        cls, raw: RawTag, strict: bool = False, parser: TagParser | None = None
    ) -> TransformTag:
        length = len(raw.params)
        if length not in (1, 2, 3, 4):
            raise ValueError(f"{cls.__name__} expected 1, 2, 3 or 4 params, got {length}")

        modifier = raw.params[-1]
        if parser is not None:
            parsed_modifier: OverrideBlock = parser.parse_block(modifier, strict=strict)
        else:
            raise ValueError("TagParser is required to parse the modifier of TransformTag")

        if length == 1:
            return cls(modifier=parsed_modifier, _raw=raw)
        if length == 2:
            accel = TypeParser.parse_float(raw.params[0])
            return cls(modifier=parsed_modifier, accel=accel, _raw=raw)
        if length == 3:
            t1 = TypeParser.parse_int(raw.params[0])
            t2 = TypeParser.parse_int(raw.params[1])
            return cls(modifier=parsed_modifier, t1=t1, t2=t2, _raw=raw)
        if length == 4:
            t1 = TypeParser.parse_int(raw.params[0])
            t2 = TypeParser.parse_int(raw.params[1])
            accel = TypeParser.parse_float(raw.params[2])
            return cls(
                modifier=parsed_modifier,
                t1=t1,
                t2=t2,
                accel=accel,
                _raw=raw,
            )
        assert False, "Unreachable"

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
