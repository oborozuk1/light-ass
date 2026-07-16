from __future__ import annotations

from collections.abc import Iterable, Iterator
from copy import deepcopy
from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, TypeVar, overload

from ..types import AssShape
from .override_block import OverrideBlock
from .tags import RawTag, Tag
from .tags.base import EffectGroup

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


BracedNode = RawTag | Tag | CommentNode
BareNode = TextNode | DrawingNode | EscapeNode
Node = BracedNode | BareNode
LinePart = OverrideBlock | BareNode

_TagT = TypeVar("_TagT", bound=Tag)


class ParsedLine:
    def __init__(self, parts: list[LinePart]) -> None:
        self.parts: list[LinePart] = parts

    def __len__(self) -> int:
        return len(self.parts)

    def __iter__(self) -> Iterator[Node]:
        for part in self.parts:
            if isinstance(part, OverrideBlock):
                yield from part
            else:
                yield part

    def __reversed__(self) -> Iterator[LinePart]:
        return reversed(self.parts)

    def __getitem__(self, item: int | slice) -> LinePart | list[LinePart]:
        return self.parts[item]

    def get_text(self) -> str:
        return "".join(part.to_ass() for part in self.parts)

    def get_plain_text(self, keep_escape_nodes: bool = False) -> str:
        if keep_escape_nodes:
            return "".join(p.to_ass() for p in self.parts if isinstance(p, (TextNode, EscapeNode)))
        return "".join(p.text for p in self.parts if isinstance(p, TextNode))

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
        tag_cls: type[_TagT] | tuple[type[_TagT], ...] | None = None,
        include_transformed_tags: bool = True,
    ) -> list[_TagT]:
        tags = []
        for part in self.parts:
            if isinstance(part, OverrideBlock):
                tags.extend(part.get_tags(tag_cls, include_transformed_tags))
        return tags

    def insert(self, index: int, parts: LinePart | Iterable[LinePart]) -> None:
        if not isinstance(parts, Iterable):
            parts = [parts]
        self.parts[index:index] = parts

    def resolve(self, style: Style, doc: Document) -> ParsedLine:
        original_style = style
        parts: list[LinePart] = []
        fontsize_state: float = style.fontsize
        for part in self.parts:
            if isinstance(part, OverrideBlock):
                new_block, style, fontsize_state = part.resolve(style, doc, original_style, fontsize_state)
                parts.append(new_block)
            else:
                parts.append(deepcopy(part))
        return ParsedLine(parts)

    def collect_effective_indices(self) -> dict[EffectGroup, set[tuple[int, int]]]:
        groups: dict[EffectGroup, list[list[tuple[Tag, int]]]] = {}
        for part_idx, part in enumerate(self.parts):
            if not isinstance(part, OverrideBlock):
                continue
            for group, tags in part.collect_effective_indices().items():
                groups.setdefault(group, list([] for _ in range(len(self.parts))))
                groups[group][part_idx].extend(tags)

        return {
            group: group.policy.simplify_across_blocks(blocks)
            for group, blocks in groups.items()
        }

    def get_effective(self, group_name: str) -> list[Tag]:
        target = None
        keep: set[tuple[int, int]] = set()
        for group, indices in self.collect_effective_indices().items():
            if group.name == group_name:
                target = group
                keep = indices
                break

        if target is None:
            return []

        effective: list[Tag] = []
        for part_idx, part in enumerate(self.parts):
            if not isinstance(part, OverrideBlock):
                continue
            for idx, tag in enumerate(part.nodes):
                if isinstance(tag, Tag) and (part_idx, idx) in keep:
                    effective.append(tag)

        return effective

    def merge_adjacent_override_blocks(self) -> None:
        merged: list[LinePart] = []
        pending: list[TextNode] = []
        for part in self.parts:
            if isinstance(part, OverrideBlock):
                if merged and isinstance(merged[-1], OverrideBlock):
                    merged[-1].nodes.extend(part.nodes)
                    pending.clear()
                else:
                    merged.extend(pending)
                    pending.clear()
                    merged.append(part)
            elif isinstance(part, TextNode) and not part.text:
                pending.append(part)
            else:
                merged.extend(pending)
                pending.clear()
                merged.append(part)
        merged.extend(pending)
        self.parts = merged

    def simplify(
        self,
        keep_raw_tag: bool = True,
        keep_comment_node: bool = False,
        keep_invalid_tags: bool = False
    ) -> None:
        self.merge_adjacent_override_blocks()

        for part in self.parts:
            if isinstance(part, OverrideBlock):
                part.simplify(keep_raw_tag, keep_comment_node, keep_invalid_tags)

        keep = set().union(*self.collect_effective_indices().values())

        for part_idx, part in enumerate(self.parts):
            if not isinstance(part, OverrideBlock):
                continue
            part.nodes = [
                node
                for idx, node in enumerate(part.nodes)
                if not isinstance(node, Tag) or (part_idx, idx) in keep
            ]

        self.parts = [
            part for part in self.parts
            if not isinstance(part, OverrideBlock) or len(part.nodes) > 0
        ]

    def to_ass(self) -> str:
        return self.get_text()
