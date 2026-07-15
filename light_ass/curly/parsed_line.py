from __future__ import annotations

from collections.abc import Iterator, Iterable
from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from ..types import AssShape
from .tags import (
    AlignmentTag,
    AlphaTag,
    BlurEdgeTag,
    BlurTag,
    BoldSimpleTag,
    BoldTag,
    BorderTag,
    BorderXTag,
    BorderYTag,
    DrawingBaselineOffsetTag,
    DrawingModeTag,
    FontEncodingTag,
    FontNameTag,
    FontSizeAbsoluteTag,
    FontSizeTag,
    ItalicTag,
    KaraokeOutlineTag,
    KaraokeSweepTag,
    KaraokeTag,
    KaraokeTimeTag,
    LegacyAlignmentTag,
    LetterSpacingTag,
    OutlineAlphaTag,
    OutlineColorTag,
    PrimaryAlphaTag,
    PrimaryColorTag,
    RawTag,
    ResetStyleTag,
    RotateXTag,
    RotateYTag,
    RotateZTag,
    ScaleTag,
    ScaleXTag,
    ScaleYTag,
    SecondaryAlphaTag,
    SecondaryColorTag,
    ShadowAlphaTag,
    ShadowColorTag,
    ShadowTag,
    ShadowXTag,
    ShadowYTag,
    ShearXTag,
    ShearYTag,
    SimpleTag,
    StrikeoutTag,
    Tag,
    UnderlineTag,
    WrapStyleTag,
    TransformTag,
    FontSizeRelativeTag,
)

if TYPE_CHECKING:
    from ..document import Document
    from ..styles import Style


@dataclass
class CommentNode:
    text: str

    def to_ass(self) -> str:
        return self.text

    def __str__(self) -> str:
        return self.text


@dataclass
class TextNode:
    text: str

    def to_ass(self) -> str:
        return self.text

    def __str__(self) -> str:
        return self.text


@dataclass
class DrawingNode:
    shape: AssShape

    def to_ass(self) -> str:
        return self.shape.to_ass()


@dataclass
class EscapeNode:
    command: ClassVar[str]
    amount: int = 1

    @classmethod
    def from_raw(cls, raw: str) -> EscapeNode:
        parts = [p for p in raw.split("\\") if p]
        if all(p == "N" for p in parts):
            return NewlineNode(len(parts))
        if all(p == "n" for p in parts):
            return SoftNewlineNode(len(parts))
        if all(p == "h" for p in parts):
            return HardSpaceNode(len(parts))
        raise ValueError(f"Unrecognized escape pattern: {raw!r}")

    def to_ass(self) -> str:
        return self.command * self.amount


@dataclass
class NewlineNode(EscapeNode):
    command: ClassVar[str] = "\\N"


@dataclass
class SoftNewlineNode(EscapeNode):
    command: ClassVar[str] = "\\n"


@dataclass
class HardSpaceNode(EscapeNode):
    command: ClassVar[str] = "\\h"


InBraceNode = RawTag | Tag | CommentNode
OutBraceNode = TextNode | DrawingNode | EscapeNode
Segment = InBraceNode | OutBraceNode


@dataclass
class ParsedLine:
    parts: list[Segment]

    def __len__(self) -> int:
        return len(self.parts)

    def __iter__(self) -> Iterator[Segment]:
        return iter(self.parts)

    def get_text(self) -> str:
        result = []
        in_brace = False
        for part in self.parts:
            if isinstance(part, InBraceNode) and not in_brace:
                result.append("{")
                in_brace = True
            elif isinstance(part, OutBraceNode) and in_brace:
                result.append("}")
                in_brace = False
            result.append(part.to_ass())
        if in_brace:
            result.append("}")
        return "".join(result)

    def get_plain_text(self, keep_escape_nodes: bool = False) -> str:
        if keep_escape_nodes:
            return "".join(p.to_ass() for p in self.parts if isinstance(p, (TextNode, EscapeNode)))
        return "".join(p.text for p in self.parts if isinstance(p, TextNode))

    def get_tags(self, tag_cls: type[Tag] | Iterable[type[Tag]] | None = None) -> list[Tag]:
        if tag_cls is None:
            tag_cls = (Tag,)
        if not isinstance(tag_cls, Iterable):
            tag_cls = (tag_cls,)
        return [p for p in self.parts if isinstance(p, tuple(tag_cls))]

    def insert(self, index: int, tags: Segment | Iterable[Segment]) -> None:
        if not isinstance(tags, Iterable):
            tags = [tags]
        self.parts[index:index] = tags

    def resolve(self, style: Style, doc: Document) -> ParsedLine:
        original_style = style
        segments = []
        fontsize_state: float = style.fontsize
        for tag in self.parts:
            if not isinstance(tag, SimpleTag):
                if isinstance(tag, TransformTag):
                    tag.modifier = ParsedLine(tag.modifier).resolve(style, doc).parts
                    for t in reversed(tag.modifier):
                        if isinstance(t, FontSizeAbsoluteTag):
                            fontsize_state = t.value
                            break
                segments.append(tag)
                continue
            if tag.value is not None:
                match tag:
                    case ResetStyleTag():
                        style = doc.styles[tag.value]
                        segments.append(tag)
                    case FontSizeRelativeTag():
                        val = fontsize_state * (1 + tag.value / 10)
                        segments.append(FontSizeAbsoluteTag(val))
                        fontsize_state = val
                    case AlphaTag():
                        segments.append(PrimaryAlphaTag(tag.value))
                        segments.append(SecondaryAlphaTag(tag.value))
                        segments.append(OutlineAlphaTag(tag.value))
                        segments.append(ShadowAlphaTag(tag.value))
                    case _:
                        segments.append(tag)
                continue
            match tag:
                case AlphaTag():
                    segments.append(PrimaryAlphaTag(style.alpha1))
                    segments.append(SecondaryAlphaTag(style.alpha2))
                    segments.append(OutlineAlphaTag(style.alpha3))
                    segments.append(ShadowAlphaTag(style.alpha4))
                case AlignmentTag():
                    segments.append(AlignmentTag(style.alignment))
                case BlurEdgeTag():
                    segments.append(BlurEdgeTag(0))
                case BlurTag():
                    segments.append(BlurTag(0))
                case BoldTag():
                    segments.append(BoldSimpleTag(style.bold))
                case BorderTag():
                    segments.append(BorderTag(style.outline))
                case BorderXTag():
                    segments.append(BorderXTag(style.outline))
                case BorderYTag():
                    segments.append(BorderYTag(style.outline))
                case DrawingBaselineOffsetTag():
                    segments.append(DrawingBaselineOffsetTag(0))
                case DrawingModeTag():
                    segments.append(DrawingModeTag(0))
                case FontEncodingTag():
                    segments.append(FontEncodingTag(style.encoding))
                case FontNameTag():
                    segments.append(FontNameTag(style.fontname))
                case FontSizeTag():
                    segments.append(FontSizeAbsoluteTag(style.fontsize))
                case ItalicTag():
                    segments.append(ItalicTag(style.italic))
                case KaraokeOutlineTag():
                    segments.append(KaraokeOutlineTag(100))
                case KaraokeSweepTag():
                    segments.append(KaraokeSweepTag(100))
                case KaraokeTag():
                    segments.append(KaraokeTag(100))
                case KaraokeTimeTag():
                    segments.append(KaraokeTimeTag(100))
                case LegacyAlignmentTag():
                    segments.append(AlignmentTag(style.alignment))
                case LetterSpacingTag():
                    segments.append(LetterSpacingTag(style.spacing))
                case OutlineAlphaTag():
                    segments.append(OutlineAlphaTag(style.alpha3))
                case OutlineColorTag():
                    segments.append(OutlineColorTag(style.color3))
                case PrimaryAlphaTag():
                    segments.append(PrimaryAlphaTag(style.alpha1))
                case PrimaryColorTag():
                    segments.append(PrimaryColorTag(style.color1))
                case ResetStyleTag():
                    segments.append(ResetStyleTag(original_style.name))
                case RotateXTag():
                    segments.append(RotateXTag(style.angle))
                case RotateYTag():
                    segments.append(RotateYTag(0))
                case RotateZTag():
                    segments.append(RotateZTag(0))
                case ScaleTag():
                    segments.append(ScaleXTag(style.scale_x))
                    segments.append(ScaleYTag(style.scale_y))
                case ScaleXTag():
                    segments.append(ScaleXTag(style.scale_x))
                case ScaleYTag():
                    segments.append(ScaleYTag(style.scale_y))
                case SecondaryAlphaTag():
                    segments.append(SecondaryAlphaTag(style.alpha2))
                case SecondaryColorTag():
                    segments.append(SecondaryColorTag(style.color2))
                case ShadowAlphaTag():
                    segments.append(ShadowAlphaTag(style.alpha4))
                case ShadowColorTag():
                    segments.append(ShadowColorTag(style.color4))
                case ShadowTag():
                    segments.append(ShadowTag(style.shadow))
                case ShadowXTag():
                    segments.append(ShadowXTag(style.shadow))
                case ShadowYTag():
                    segments.append(ShadowYTag(style.shadow))
                case ShearXTag():
                    segments.append(ShearXTag(0))
                case ShearYTag():
                    segments.append(ShearYTag(0))
                case StrikeoutTag():
                    segments.append(StrikeoutTag(style.strike_out))
                case UnderlineTag():
                    segments.append(UnderlineTag(style.underline))
                case WrapStyleTag():
                    segments.append(WrapStyleTag(doc.info.get("WrapStyle", 0)))
        return ParsedLine(segments)

    def to_ass(self) -> str:
        return self.get_text()
