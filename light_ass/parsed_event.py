from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from .curly import ParsedLine, Tag
from .curly.tags import MoveTag, PositionTag
from .events import Dialog
from .types import AssTime, Point
from .types.align import Align

if TYPE_CHECKING:
    from .document import Document
    from .styles import Style

_TagT = TypeVar("_TagT", bound=Tag)

def _alignment_x(alignment: Align, width: int, margin_l: int, margin_r: int) -> int:
    col = (alignment - 1) % 3
    if col == 0:
        return margin_l
    if col == 1:
        return (width + margin_l - margin_r) // 2
    return width - margin_r


def _alignment_y(alignment: Align, height: int, margin_v: int) -> int:
    row = (alignment - 1) // 3
    if row == 0:
        return height - margin_v
    if row == 1:
        return height // 2
    return margin_v


class ParsedDialog:
    doc: Document
    event: Dialog
    parsed: ParsedLine
    def __init__(self, doc: Document, event: Dialog, parsed: ParsedLine) -> None:
        self.doc = doc
        self.event = event
        self.parsed = parsed
        self.comment = event.comment
        self.layer = event.layer
        self.start = event.start
        self.end = event.end
        self.style = event.style
        self.name = event.name
        self.margin_l = event.margin_l
        self.margin_r = event.margin_r
        self.margin_v = event.margin_v
        self.effect = event.effect
        self.original_text = event.text

    @property
    def text(self) -> str:
        return self.parsed.get_text()

    @property
    def plain_text(self) -> str:
        return self.parsed.get_plain_text()

    @property
    def duration(self) -> AssTime:
        return self.end - self.start

    @property
    def target_style(self) -> Style:
        return self.doc.styles[self.style]

    def get_tags(
        self,
        tag_cls: type[_TagT] | tuple[type[_TagT]] | None = None,
        include_transformed_tags: bool = True,
    ) -> list[_TagT]:
        return self.parsed.get_tags(tag_cls, include_transformed_tags)

    def get_plain_text(self, keep_escape_nodes: bool = False) -> str:
        return self.parsed.get_plain_text(keep_escape_nodes)

    def to_ass(self) -> str:
        type_ = "Dialogue" if not self.comment else "Comment"
        return (
            f"{type_}: {self.layer},{self.start},{self.end},{self.style},{self.name},"
            f"{self.margin_l},{self.margin_r},{self.margin_v},{self.effect},{self.text}"
        )

    def resolve(self) -> ParsedLine:
        return self.parsed.resolve(self.target_style, self.doc)

    def get_margin(self) -> tuple[int, int, int]:
        margin_l = self.margin_l or self.target_style.margin_l
        margin_r = self.margin_r or self.target_style.margin_r
        margin_v = self.margin_v or self.target_style.margin_v
        return margin_l, margin_r, margin_v

    def get_alignment(self) -> Align:
        alignment = self.resolve().get_effective("alignment")
        if alignment:
            return alignment[0].value
        return self.target_style.alignment

    def get_position(self, at: AssTime | int | None = None) -> Point:
        at = int(at) if at is not None else 0
        tags = self.parsed.get_effective("position")
        if tags:
            tag = tags[0]
            if isinstance(tag, PositionTag):
                return tag.point
            if isinstance(tag, MoveTag):
                start = tag.start
                end = tag.end
                t1 = tag.t1 or 0
                t2 = tag.t2 or 0
                if t1 <= 0 and t2 <= 0:
                    t1 = 0
                    t2 = int(self.end)
                delta = t2 - t1
                t = at - int(self.start)
                if t <= t1:
                    k = 0.0
                elif t >= t2:
                    k = 1.0
                else:
                    k = (t - t1) / delta
                return (end - start) * k

        style = self.doc.styles[self.style]
        play_res_x = self.doc.info.get("PlayResX", 1920)
        play_res_y = self.doc.info.get("PlayResY", 1080)
        left, right, vertical = self.get_margin()
        alignment = style.alignment

        x = _alignment_x(alignment, play_res_x, left, right)
        y = _alignment_y(alignment, play_res_y, vertical)
        return Point(x, y)

    def submit(self) -> None:
        self.event.comment = self.comment
        self.event.layer = self.layer
        self.event.start = self.start
        self.event.end = self.end
        self.event.style = self.style
        self.event.name = self.name
        self.event.margin_l = self.margin_l
        self.event.margin_r = self.margin_r
        self.event.margin_v = self.margin_v
        self.event.effect = self.effect
        self.event.text = self.text
