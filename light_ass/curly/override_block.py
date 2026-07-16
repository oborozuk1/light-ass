from __future__ import annotations

from collections.abc import Iterator
from copy import deepcopy
from typing import TYPE_CHECKING, TypeVar, overload

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
    FontSizeRelativeTag,
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
    TransformTag,
    UnderlineTag,
    WrapStyleTag,
)
from .tags.base import EffectGroup

if TYPE_CHECKING:
    from ..document import Document
    from ..styles import Style
    from .parsed_line import BracedNode

_TagT = TypeVar("_TagT", bound=Tag)


def get_tags(
    nodes: list[BracedNode],
    tag_types: tuple[type[Tag], ...] | tuple[type[_TagT], ...],
    include_transformed_tags: bool = True,
) -> list[Tag]:
    from .tags import TransformTag

    result = []
    for part in nodes:
        if isinstance(part, tag_types):
            result.append(part)
        if isinstance(part, TransformTag) and include_transformed_tags:
            for tag in part.modifier:
                if isinstance(tag, tag_types):
                    result.append(tag)
    return result


class OverrideBlock:
    def __init__(self, tags: list[BracedNode] | None = None):
        self.nodes: list[BracedNode] = tags if tags is not None else []

    def __len__(self) -> int:
        return len(self.nodes)

    def __iter__(self) -> Iterator[BracedNode]:
        return iter(self.nodes)

    def __reversed__(self) -> Iterator[BracedNode]:
        return reversed(self.nodes)

    @overload
    def __getitem__(self, idx: int) -> BracedNode: ...
    @overload
    def __getitem__(self, idx: slice) -> list[BracedNode]: ...
    def __getitem__(self, item: int | slice) -> BracedNode | list[BracedNode]:
        return self.nodes[item]

    def __repr__(self) -> str:
        return repr(self.nodes)

    @overload
    def get_tags(
        self,
        tag_cls: None = None,
        include_transformed_tags: bool = True,
    ) -> list[Tag]: ...

    @overload
    def get_tags(
        self,
        tag_cls: type[_TagT] | tuple[type[_TagT], ...],
        include_transformed_tags: bool = True,
    ) -> list[_TagT]: ...

    def get_tags(
        self,
        tag_cls: type[Tag] | tuple[type[Tag], ...] | None = None,
        include_transformed_tags: bool = True,
    ) -> list[Tag]:
        if tag_cls is None:
            tag_cls = (Tag,)
        elif not isinstance(tag_cls, tuple):
            tag_cls = (tag_cls,)
        return get_tags(self.nodes, tag_cls, include_transformed_tags)

    def to_ass(self, include_brace: bool = True) -> str:
        tags_str = "".join(tag.to_ass() for tag in self.nodes)
        if include_brace:
            return f"{{{tags_str}}}"
        return tags_str

    def resolve(
        self,
        style: Style,
        doc: Document,
        original_style: Style | None = None,
        fontsize_state: float | None = None
    ) -> tuple[OverrideBlock, Style, float]:
        if original_style is None:
            original_style = style
        if fontsize_state is None:
            fontsize_state = style.fontsize

        nodes: list[BracedNode] = []
        wrap_style = doc.info.get("WrapStyle", 0)
        for tag in self.nodes:
            if not isinstance(tag, SimpleTag):
                if isinstance(tag, TransformTag):
                    tag.modifier, style, fontsize_state = tag.modifier.resolve(
                        style, doc, original_style, fontsize_state)
                    for t in reversed(tag.modifier):
                        if isinstance(t, FontSizeAbsoluteTag):
                            fontsize_state = t.value
                            break
                t = deepcopy(tag)
                if isinstance(t, Tag):
                    t.normalize()
                nodes.append(t)
                continue
            if tag.value is not None:
                match tag:
                    case ResetStyleTag():
                        style = doc.styles[tag.value]
                        fontsize_state = style.fontsize
                        nodes.append(deepcopy(tag))
                    case FontSizeRelativeTag():
                        val = fontsize_state * (1 + tag.value / 10)
                        nodes.append(FontSizeAbsoluteTag(val))
                        fontsize_state = val
                    case AlphaTag():
                        nodes.append(PrimaryAlphaTag(tag.value))
                        nodes.append(SecondaryAlphaTag(tag.value))
                        nodes.append(OutlineAlphaTag(tag.value))
                        nodes.append(ShadowAlphaTag(tag.value))
                    case _:
                        nodes.append(deepcopy(tag))
                continue
            match tag:
                case AlphaTag():
                    nodes.append(PrimaryAlphaTag(style.alpha1))
                    nodes.append(SecondaryAlphaTag(style.alpha2))
                    nodes.append(OutlineAlphaTag(style.alpha3))
                    nodes.append(ShadowAlphaTag(style.alpha4))
                case AlignmentTag():
                    nodes.append(AlignmentTag(style.alignment))
                case BlurEdgeTag():
                    nodes.append(BlurEdgeTag(0))
                case BlurTag():
                    nodes.append(BlurTag(0))
                case BoldTag():
                    nodes.append(BoldSimpleTag(style.bold))
                case BorderTag():
                    nodes.append(BorderTag(style.outline))
                case BorderXTag():
                    nodes.append(BorderXTag(style.outline))
                case BorderYTag():
                    nodes.append(BorderYTag(style.outline))
                case DrawingBaselineOffsetTag():
                    nodes.append(DrawingBaselineOffsetTag(0))
                case DrawingModeTag():
                    nodes.append(DrawingModeTag(0))
                case FontEncodingTag():
                    nodes.append(FontEncodingTag(style.encoding))
                case FontNameTag():
                    nodes.append(FontNameTag(style.fontname))
                case FontSizeTag():
                    nodes.append(FontSizeAbsoluteTag(style.fontsize))
                case ItalicTag():
                    nodes.append(ItalicTag(style.italic))
                case KaraokeOutlineTag():
                    nodes.append(KaraokeOutlineTag(100))
                case KaraokeSweepTag():
                    nodes.append(KaraokeSweepTag(100))
                case KaraokeTag():
                    nodes.append(KaraokeTag(100))
                case KaraokeTimeTag():
                    nodes.append(KaraokeTimeTag(100))
                case LegacyAlignmentTag():
                    nodes.append(AlignmentTag(style.alignment))
                case LetterSpacingTag():
                    nodes.append(LetterSpacingTag(style.spacing))
                case OutlineAlphaTag():
                    nodes.append(OutlineAlphaTag(style.alpha3))
                case OutlineColorTag():
                    nodes.append(OutlineColorTag(style.color3))
                case PrimaryAlphaTag():
                    nodes.append(PrimaryAlphaTag(style.alpha1))
                case PrimaryColorTag():
                    nodes.append(PrimaryColorTag(style.color1))
                case ResetStyleTag():
                    nodes.append(ResetStyleTag(original_style.name))
                case RotateXTag():
                    nodes.append(RotateXTag(style.angle))
                case RotateYTag():
                    nodes.append(RotateYTag(0))
                case RotateZTag():
                    nodes.append(RotateZTag(0))
                case ScaleTag():
                    nodes.append(ScaleXTag(style.scale_x))
                    nodes.append(ScaleYTag(style.scale_y))
                case ScaleXTag():
                    nodes.append(ScaleXTag(style.scale_x))
                case ScaleYTag():
                    nodes.append(ScaleYTag(style.scale_y))
                case SecondaryAlphaTag():
                    nodes.append(SecondaryAlphaTag(style.alpha2))
                case SecondaryColorTag():
                    nodes.append(SecondaryColorTag(style.color2))
                case ShadowAlphaTag():
                    nodes.append(ShadowAlphaTag(style.alpha4))
                case ShadowColorTag():
                    nodes.append(ShadowColorTag(style.color4))
                case ShadowTag():
                    nodes.append(ShadowTag(style.shadow))
                case ShadowXTag():
                    nodes.append(ShadowXTag(style.shadow))
                case ShadowYTag():
                    nodes.append(ShadowYTag(style.shadow))
                case ShearXTag():
                    nodes.append(ShearXTag(0))
                case ShearYTag():
                    nodes.append(ShearYTag(0))
                case StrikeoutTag():
                    nodes.append(StrikeoutTag(style.strike_out))
                case UnderlineTag():
                    nodes.append(UnderlineTag(style.underline))
                case WrapStyleTag():
                    nodes.append(WrapStyleTag(wrap_style))

        return OverrideBlock(nodes), style, fontsize_state  # type:ignore[return-value]

    def collect_effective_indices(self) -> dict[EffectGroup, list[tuple[Tag, int]]]:
        groups: dict[EffectGroup, list[tuple[Tag, int]]] = {}
        for idx, node in enumerate(self.nodes):
            if isinstance(node, Tag):
                groups.setdefault(node.effect_group, []).append((node, idx))
        result: dict[EffectGroup, list[tuple[Tag, int]]] = {}
        for group, tags in groups.items():
            keep = group.policy.simplify_in_block(tags)
            result[group] = [item for item in tags if item[1] in keep]
        return result

    def get_effective(self, group_name: str) -> list[Tag]:
        for group, tags in self.collect_effective_indices().items():
            if group.name == group_name:
                return [tag for tag, _ in tags]
        return []

    def simplify(
        self,
        keep_raw_tag: bool = True,
        keep_comment_node: bool = False,
        keep_invalid_tags: bool = False
    ) -> None:
        from .parsed_line import CommentNode

        non_tag_keep = set()
        for idx, node in enumerate(self.nodes):
            if isinstance(node, RawTag) and not keep_raw_tag:
                continue
            if isinstance(node, RawTag) and not keep_invalid_tags and node.cls:
                continue
            if isinstance(node, CommentNode) and not keep_comment_node:
                continue
            if not isinstance(node, Tag):
                non_tag_keep.add(idx)

        keep = non_tag_keep.union(
            idx for tags in self.collect_effective_indices().values() for _, idx in tags
        )
        self.nodes = [node for idx, node in enumerate(self.nodes) if idx in keep]
