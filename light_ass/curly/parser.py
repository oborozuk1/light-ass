from __future__ import annotations

import re
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from typing import Any, ClassVar

from ..types import AssShape
from .tags import STANDARD_TAG_SET, DrawingModeTag, RawTag, SimpleTag, Tag


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

    def get_plain_text(self) -> str:
        return "".join(p.text for p in self.parts if isinstance(p, TextNode))

    def get_tags(self) -> list[Tag]:
        return [p for p in self.parts if isinstance(p, Tag)]

    def to_ass(self) -> str:
        return self.get_text()


class TagParser:
    _BLOCK_ESCAPED_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"(?<!\\){(.*?)}")
    _BLOCK_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"{(.*?)}")
    _TAG_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"\\([^(\\]+)(?:\(([^)]*)\)?)?")

    _ESCAPE_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"((?:\\N)+|(?:\\n)+|(?:\\h)+)")

    _tag_set: frozenset[type[Tag]]
    _registry: dict[str, type[Tag]]
    _tag_name_set: frozenset[str]
    _max_len: int
    _frozen: bool

    def __init__(
        self,
        tag_set: Iterable[type[Tag]] | None = None,
        strict: bool = False,
        escape_brace: bool = True,
        parse_escape_nodes: bool = False,
    ):
        if tag_set is None:
            tag_set = STANDARD_TAG_SET
        self.strict = strict
        self.escape_brace = escape_brace
        self.parse_escape_nodes = parse_escape_nodes
        self.update_tag_set(tag_set)
        self._frozen = False

    def freeze(self) -> None:
        self._frozen = True

    def unfreeze(self) -> None:
        self._frozen = False

    def __setattr__(self, name: str, value: Any) -> None:
        if self.__dict__.get("_frozen") and name != "_frozen":
            raise AttributeError(f"Can't set attribute {name!r}")
        super().__setattr__(name, value)

    def update_tag_set(self, tag_set: Iterable[type[Tag]]) -> None:
        self._tag_set = frozenset(tag_set)
        self._build_registry()

    @staticmethod
    def split_params(raw: str) -> list[str]:
        first, sep, rest = raw.partition("\\")
        parts = [x.strip(" \t") for x in first.split(",") if x.strip(" \t")]
        if sep:
            parts.append("\\" + rest)
        return parts

    def _build_registry(self) -> None:
        registry = {}
        for t in self._tag_set:
            if t.tag_name in registry:
                raise ValueError(f"Duplicate tag name: {t.tag_name!r}")
            registry[t.tag_name] = t
            for alias in t.aliases:
                registry[alias] = t
        self._registry = registry
        self._tag_name_set = frozenset(registry.keys())
        self._max_len = max(len(tag_name) for tag_name in self._tag_name_set)

    def find_tag_cls(self, cmd: str) -> tuple[str, type[Tag]] | None:
        if self._registry.get(cmd):
            return cmd, self._registry[cmd]

        n = min(self._max_len, len(cmd))
        for i in range(n, 0, -1):
            name = cmd[:i]
            if name in self._tag_name_set:
                return name, self._registry[name]
        return None

    def parse_block(self, block_str: str, strict: bool | None = None) -> list[InBraceNode]:
        if not self._registry:
            self._build_registry()
        if strict is None:
            strict = self.strict

        if strict and block_str.find("{") != -1:
            raise ValueError(f"Braces are not allowed in strict mode: {block_str!r}")

        length = len(block_str)
        raw_tags: list[RawTag | CommentNode] = []
        prev_pos = 0
        for tag_match in self._TAG_PATTERN.finditer(block_str):
            start, end = tag_match.span()
            if prev_pos < start:
                raw_tags.append(CommentNode(block_str[prev_pos:start]))
            prev_pos = end
            cmd = tag_match.group(1)
            raw_params = tag_match.group(2) or ""
            raw_text = tag_match.group(0)

            for _ in range(raw_params.count("(")):
                if prev_pos >= length or block_str[prev_pos] != ")":
                    break
                prev_pos += 1

            if prev_pos > end:
                suffix = block_str[end:prev_pos]
                raw_text += suffix
                raw_params += suffix

            params = self.split_params(raw_params)

            result = self.find_tag_cls(cmd)

            if result is None:
                raw_tags.append(RawTag(cmd, tuple(params), raw_text, None))
                continue

            tag_name, tag_cls = result

            if issubclass(tag_cls, SimpleTag):
                if param := cmd[len(tag_name) :]:
                    params.append(param)

            raw_tags.append(RawTag(tag_name, tuple(params), raw_text, tag_cls))

        if prev_pos < length:
            raw_tags.append(CommentNode(block_str[prev_pos:]))

        tags: list[InBraceNode] = []
        for raw_tag in raw_tags:
            if isinstance(raw_tag, CommentNode):
                tags.append(raw_tag)
                continue
            try:
                if raw_tag.cls is None:
                    raise ValueError(f"Unknown tag name: {raw_tag.name!r}")
                else:
                    tag = raw_tag.cls.from_raw(raw_tag, strict=strict, parser=self)
                    tags.append(tag)
            except ValueError as e:
                if strict:
                    raise e
                tags.append(raw_tag)

        return tags

    def parse(
        self,
        line: str,
        strict: bool | None = None,
        escape_brace: bool | None = None,
        parse_escape_nodes: bool | None = None,
    ) -> ParsedLine:
        if escape_brace is None:
            escape_brace = self.escape_brace
        if parse_escape_nodes is None:
            parse_escape_nodes = self.parse_escape_nodes

        pattern = self._BLOCK_ESCAPED_PATTERN if escape_brace else self._BLOCK_PATTERN
        segments = pattern.split(line)

        parts: list[Segment] = []
        drawing_scale = 0
        for idx, segment in enumerate(segments):
            if idx % 2 == 1:
                tags = self.parse_block(segment, strict=strict)
                parts.extend(tags)
                for tag in tags:
                    if isinstance(tag, DrawingModeTag):
                        drawing_scale = tag.value if tag.value is not None and tag.value >= 0 else 0
                continue
            if not segment and idx == 0:
                continue
            if drawing_scale > 0:
                parts.append(DrawingNode(AssShape.from_ass(segment)))
            elif parse_escape_nodes:
                p = self._ESCAPE_PATTERN.split(segment)
                if len(p) == 1:
                    parts.append(TextNode(segment))
                    continue
                for i, text_part in enumerate(p):
                    if i % 2 == 1:
                        parts.append(EscapeNode.from_raw(text_part))
                    elif text_part:
                        parts.append(TextNode(text_part))
            else:
                parts.append(TextNode(segment))

        return ParsedLine(parts=parts)
