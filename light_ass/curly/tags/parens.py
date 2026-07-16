from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Self

from ...types.ass_shape import AssShape
from ...types.point import Point
from ...utils import Formatter, TypeParser
from .base import EffectGroup, EffectPolicy, FirstPolicy, ParensTag, RawTag, Tag

if TYPE_CHECKING:
    from ..parser import TagParser


class ClipPolicy(EffectPolicy):
    @staticmethod
    def simplify_in_block(tags: list[tuple[Tag, int]]) -> set[int]:
        result: list[int | None] = [None, None]
        for tag, idx in tags:
            if isinstance(tag, (ClipRectTag, InverseClipRectTag)):
                if result[0] is None:
                    result[0] = idx
            elif isinstance(tag, (ClipShapeTag, InverseClipShapeTag)):
                if result[1] is None:
                    result[1] = idx
        return set(v for v in result if v is not None)

    @staticmethod
    def simplify_across_blocks(blocks: list[list[tuple[Tag, int]]]) -> set[tuple[int, int]]:
        result: list[tuple[int, int] | None] = [None, None]
        for p, block in enumerate(blocks):
            for tag, idx in block:
                if isinstance(tag, (ClipRectTag, InverseClipRectTag)):
                    if result[0] is None:
                        result[0] = (p, idx)
                elif isinstance(tag, (ClipShapeTag, InverseClipShapeTag)):
                    if result[1] is None:
                        result[1] = (p, idx)
        return set(v for v in result if v is not None)


def _parse_clip_params(
    raw: RawTag,
    rect_cls: type[Any],
    shape_cls: type[Any],
    cls_name: str,
) -> Any:
    length = len(raw.params)
    if length not in (1, 2, 4):
        raise ValueError(f"{cls_name} expected 1, 2, or 4 params, got {length}")

    if length == 4:
        x1 = TypeParser.parse_float(raw.params[0])
        y1 = TypeParser.parse_float(raw.params[1])
        x2 = TypeParser.parse_float(raw.params[2])
        y2 = TypeParser.parse_float(raw.params[3])
        return rect_cls(x1, y1, x2, y2, _raw=raw)

    shape = AssShape.from_ass(raw.params[-1])
    scale = TypeParser.parse_int(raw.params[0]) if length == 2 else None
    return shape_cls(shape, scale, _raw=raw)


@dataclass
class PositionTag(ParensTag):
    tag_name = "pos"
    effect_group = EffectGroup("position", FirstPolicy)
    x: float
    y: float

    @classmethod
    def from_raw(cls, raw: RawTag, strict: bool = False, parser: TagParser | None = None) -> Self:
        if len(raw.params) != 2:
            raise ValueError(f"{cls.__name__} expected 2 params, got {len(raw.params)}")
        params = raw.params
        x = TypeParser.parse_float(params[0])
        y = TypeParser.parse_float(params[1])
        return cls(x, y, _raw=raw)

    def get_params(self) -> tuple[float, float]:
        return self.x, self.y

    @property
    def point(self) -> Point:
        return Point(self.x, self.y)


@dataclass
class MoveTag(ParensTag):
    tag_name = "move"
    effect_group = EffectGroup("position", FirstPolicy)
    x1: float
    y1: float
    x2: float
    y2: float
    t1: int | None = None
    t2: int | None = None

    @classmethod
    def from_raw(cls, raw: RawTag, strict: bool = False, parser: TagParser | None = None) -> Self:
        length = len(raw.params)

        if length not in (4, 6):
            raise ValueError(f"{cls.__name__} expected 4 or 6 params, got {len(raw.params)}")

        x1 = TypeParser.parse_float(raw.params[0])
        y1 = TypeParser.parse_float(raw.params[1])
        x2 = TypeParser.parse_float(raw.params[2])
        y2 = TypeParser.parse_float(raw.params[3])

        if length == 4:
            return cls(x1, y1, x2, y2, _raw=raw)

        t1 = TypeParser.parse_int(raw.params[4])
        t2 = TypeParser.parse_int(raw.params[5])
        return cls(x1, y1, x2, y2, t1, t2, _raw=raw)

    def get_params(
        self,
    ) -> tuple[float, float, float, float] | tuple[float, float, float, float, int, int]:
        if self.t1 is None or self.t2 is None:
            return self.x1, self.y1, self.x2, self.y2
        return self.x1, self.y1, self.x2, self.y2, self.t1, self.t2

    @property
    def start(self) -> Point:
        return Point(self.x1, self.y1)

    @property
    def end(self) -> Point:
        return Point(self.x2, self.y2)


@dataclass
class ClipTag(ParensTag):
    tag_name = "clip"
    effect_group = EffectGroup("clip", ClipPolicy)

    @classmethod
    def from_raw(
        cls, raw: RawTag, strict: bool = False, parser: TagParser | None = None
    ) -> ClipRectTag | ClipShapeTag:
        return _parse_clip_params(raw, ClipRectTag, ClipShapeTag, cls.__name__)  # type: ignore[no-any-return]


@dataclass
class ClipRectTag(ClipTag):
    x1: float
    y1: float
    x2: float
    y2: float

    def get_params(self) -> tuple[float, float, float, float]:
        return self.x1, self.y1, self.x2, self.y2

    @property
    def top_left(self) -> Point:
        return Point(self.x1, self.y1)

    @property
    def bottom_right(self) -> Point:
        return Point(self.x2, self.y2)


@dataclass
class ClipShapeTag(ClipTag):
    shape: AssShape
    scale: int | None = None

    def get_params(self) -> tuple[int | None, AssShape]:
        return self.scale, self.shape

    def _serialize(self) -> str:
        return f"\\clip({self.scale},{self.shape})"


@dataclass
class InverseClipTag(ParensTag):
    tag_name = "iclip"
    effect_group = EffectGroup("clip", ClipPolicy)

    @classmethod
    def from_raw(
        cls, raw: RawTag, strict: bool = False, parser: TagParser | None = None
    ) -> InverseClipRectTag | InverseClipShapeTag:
        return _parse_clip_params(raw, InverseClipRectTag, InverseClipShapeTag, cls.__name__)  # type: ignore[no-any-return]


@dataclass
class InverseClipRectTag(InverseClipTag):
    x1: float
    y1: float
    x2: float
    y2: float

    def get_params(self) -> tuple[float, float, float, float]:
        return self.x1, self.y1, self.x2, self.y2

    @property
    def top_left(self) -> Point:
        return Point(self.x1, self.y1)

    @property
    def bottom_right(self) -> Point:
        return Point(self.x2, self.y2)


@dataclass
class InverseClipShapeTag(InverseClipTag):
    shape: AssShape
    scale: int | None = None

    def get_params(self) -> tuple[int | None, AssShape]:
        return self.scale, self.shape

    def _serialize(self) -> str:
        return f"\\iclip({self.scale},{self.shape})"


@dataclass
class FadeTag(ParensTag):
    tag_name = "fad"
    aliases = ("fade",)

    @classmethod
    def from_raw(
        cls, raw: RawTag, strict: bool = False, parser: TagParser | None = None
    ) -> FadeSimpleTag | FadeComplexTag:
        length = len(raw.params)
        if length not in (2, 7):
            raise ValueError(f"{cls.__name__} expected 2 or 7 params, got {length}")

        if length == 2:
            fade_in = TypeParser.parse_int(raw.params[0])
            fade_out = TypeParser.parse_int(raw.params[1])
            return FadeSimpleTag(fade_in, fade_out, _raw=raw)

        a1 = TypeParser.parse_int(raw.params[0])
        a2 = TypeParser.parse_int(raw.params[1])
        a3 = TypeParser.parse_int(raw.params[2])
        t1 = TypeParser.parse_int(raw.params[3])
        t2 = TypeParser.parse_int(raw.params[4])
        t3 = TypeParser.parse_int(raw.params[5])
        t4 = TypeParser.parse_int(raw.params[6])
        return FadeComplexTag(a1, a2, a3, t1, t2, t3, t4, _raw=raw)


@dataclass
class FadeSimpleTag(FadeTag):
    fade_in: int
    fade_out: int

    def get_params(self) -> tuple[int, int]:
        return self.fade_in, self.fade_out


@dataclass
class FadeComplexTag(FadeTag):
    a1: int
    a2: int
    a3: int
    t1: int
    t2: int
    t3: int
    t4: int

    def get_params(self) -> tuple[int, int, int, int, int, int, int]:
        return self.a1, self.a2, self.a3, self.t1, self.t2, self.t3, self.t4

    def _serialize(self) -> str:
        params = ",".join(map(Formatter.format, self.get_params()))
        return f"\\fade({params})"


@dataclass
class OriginTag(ParensTag):
    tag_name = "org"
    x: float
    y: float

    @classmethod
    def from_raw(cls, raw: RawTag, strict: bool = False, parser: TagParser | None = None) -> Self:
        length = len(raw.params)
        if length != 2:
            raise ValueError(f"{cls.__name__} expected 2 params, got {length}")

        x = TypeParser.parse_float(raw.params[0])
        y = TypeParser.parse_float(raw.params[1])
        return cls(x, y, _raw=raw)

    def get_params(self) -> tuple[float, float]:
        return self.x, self.y

    @property
    def point(self) -> Point:
        return Point(self.x, self.y)
