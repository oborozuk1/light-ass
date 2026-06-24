from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ...utils import TypeParser
from .base import ParensTag, RawTag

if TYPE_CHECKING:
    from ..parser import InBraceNode, TagParser


@dataclass
class TransformTag(ParensTag):
    tag_name = "t"
    modifier: list[InBraceNode] = field(default_factory=list)
    t1: int | None = None
    t2: int | None = None
    accel: float | None = None

    @classmethod
    def from_raw(
        cls, raw: RawTag, strict: bool = False, parser: TagParser | None = None
    ) -> TransformTag:
        length = len(raw.params)
        if length not in (1, 2, 3, 4):
            raise ValueError(f"{cls.__name__} expected 1, 2, 3 or 4 params, got {length}")

        modifier = raw.params[-1]
        if parser is not None:
            parsed_modifier: list[InBraceNode] = parser.parse_block(modifier, strict=strict)
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

    def get_params(
        self,
    ) -> (
        tuple[list[InBraceNode]]
        | tuple[float, list[InBraceNode]]
        | tuple[int, int, list[InBraceNode]]
        | tuple[int, int, float, list[InBraceNode]]
    ):
        params: list[list[InBraceNode] | int | float] = []
        if self.t1 is not None and self.t2 is not None:
            params.append(self.t1)
            params.append(self.t2)
        if self.accel is not None:
            params.append(self.accel)
        params.append(self.modifier)
        return tuple(params)  # type: ignore[return-value]
