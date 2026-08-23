from __future__ import annotations

import re
from collections.abc import Iterable
from functools import lru_cache
from typing import Any, ClassVar

from ..types import AssShape
from .override_block import OverrideBlock
from .parsed_line import (
    BracedNode,
    CommentNode,
    DrawingNode,
    EscapeNode,
    LinePart,
    ParsedLine,
    TextNode,
)
from .tags import STANDARD_TAG_SET, DrawingModeTag, RawTag, SimpleTag, Tag


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
        parse_escape_nodes: bool = True,
    ):
        if tag_set is None:
            tag_set = STANDARD_TAG_SET
        self.strict = strict
        self.escape_brace = escape_brace
        self.parse_escape_nodes = parse_escape_nodes
        self.tag_set = tag_set
        self._frozen = False

    def freeze(self) -> None:
        self._frozen = True

    def unfreeze(self) -> None:
        self._frozen = False

    def __setattr__(self, name: str, value: Any) -> None:
        if self.__dict__.get("_frozen") and name != "_frozen":
            raise AttributeError(f"Can't set attribute {name!r}")
        super().__setattr__(name, value)

    @property
    def tag_set(self) -> frozenset[type[Tag]]:
        return self._tag_set

    @tag_set.setter
    def tag_set(self, tag_set: Iterable[type[Tag]]) -> None:
        self._tag_set = frozenset(tag_set)
        self._build_registry()

    @staticmethod
    def split_params(raw: str) -> list[str]:
        if not raw:
            return []
        if "," not in raw and "\\" not in raw:
            raw = raw.strip(" \t")
            return [raw] if raw else []
        first, sep, rest = raw.partition("\\")
        parts = []
        for x in first.split(","):
            if x := x.strip(" \t"):
                parts.append(x)
        if sep:
            parts.append("\\" + rest)
        return parts

    @classmethod
    def split_escape_nodes(cls, text: str) -> list[EscapeNode | TextNode]:
        if "\\" not in text:
            return [TextNode(text)]
        parts = cls._ESCAPE_PATTERN.split(text)
        if len(parts) == 1:
            return [TextNode(parts[0])]
        result: list[EscapeNode | TextNode] = []
        for i, part in enumerate(parts):
            if i % 2 == 1:
                result.append(EscapeNode.from_raw(part))
            elif part:
                result.append(TextNode(part))
        return result

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
        self._find_tag_cls = lru_cache(maxsize=4096)(self._find_tag_cls_uncached)
        self._raw_tag_of = lru_cache(maxsize=65536)(self._raw_tag_of_uncached)
        self._scan_modifier = lru_cache(maxsize=1024)(self._scan_block_uncached)
        self._simple_classes = frozenset(t for t in self._tag_set if issubclass(t, SimpleTag))

    def _find_tag_cls_uncached(self, cmd: str) -> tuple[str, type[Tag]] | None:
        names = self._tag_name_set
        registry = self._registry
        for i in range(min(self._max_len, len(cmd)), 0, -1):
            name = cmd[:i]
            if name in names:
                return name, registry[name]
        return None

    def find_tag_cls(self, cmd: str) -> tuple[str, type[Tag]] | None:
        return self._find_tag_cls(cmd[: self._max_len])

    def _raw_tag_of_uncached(self, raw_text: str) -> RawTag:
        tag_match = self._TAG_PATTERN.match(raw_text)
        if tag_match is None:
            return RawTag(raw_text[1:], (), raw_text, None)
        end = tag_match.end()
        cmd, matched_params = tag_match.group(1, 2)
        raw_params = matched_params or ""

        pos = end
        n_open = raw_params.count("(")
        length = len(raw_text)
        while n_open:
            if pos >= length or raw_text[pos] != ")":
                break
            pos += 1
            n_open -= 1
        if pos > end:
            raw_params += raw_text[end:pos]

        params = self.split_params(raw_params)

        result = self.find_tag_cls(cmd)
        if result is None:
            return RawTag(cmd, tuple(params), raw_text, None)

        tag_name, tag_cls = result
        if tag_cls in self._simple_classes:
            if param := cmd[len(tag_name) :]:
                params.append(param)
        return RawTag(tag_name, tuple(params), raw_text, tag_cls)

    def _scan_block_uncached(self, block_str: str) -> tuple[RawTag | CommentNode, ...]:
        length = len(block_str)
        raw_tags: list[RawTag | CommentNode] = []
        append = raw_tags.append
        prev_pos = 0
        finditer = self._TAG_PATTERN.finditer
        raw_tag_of = self._raw_tag_of
        for tag_match in finditer(block_str):
            start, end = tag_match.span()
            if prev_pos < start:
                append(CommentNode(block_str[prev_pos:start]))
            prev_pos = end
            matched_params = tag_match[2]

            if matched_params is not None:
                n_open = matched_params.count("(")
                while n_open:
                    if prev_pos >= length or block_str[prev_pos] != ")":
                        break
                    prev_pos += 1
                    n_open -= 1

            append(raw_tag_of(block_str[start:prev_pos]))

        if prev_pos < length:
            append(CommentNode(block_str[prev_pos:]))

        return tuple(raw_tags)

    def _instantiate_block(
        self, raw_tags: tuple[RawTag | CommentNode, ...], strict: bool
    ) -> OverrideBlock:
        tags: list[BracedNode] = []
        append = tags.append
        for raw_tag in raw_tags:
            if isinstance(raw_tag, CommentNode):
                append(raw_tag)
                continue
            if raw_tag.cls is None:
                if strict:
                    raise ValueError(f"Unknown tag name: {raw_tag.name!r}")
                append(raw_tag)
                continue
            try:
                append(raw_tag.cls.from_raw(raw_tag, strict=strict, parser=self))
            except ValueError as e:
                if strict:
                    raise e
                append(raw_tag)
        return OverrideBlock(tags)

    def parse_block(self, block_str: str, strict: bool | None = None) -> OverrideBlock:
        if strict is None:
            strict = self.strict

        if strict and block_str.find("{") != -1:
            raise ValueError(f"Braces are not allowed in strict mode: {block_str!r}")

        return self._instantiate_block(self._scan_block_uncached(block_str), strict)

    def parse_modifier(self, modifier: str, strict: bool | None = None) -> OverrideBlock:
        if strict is None:
            strict = self.strict

        if strict and modifier.find("{") != -1:
            raise ValueError(f"Braces are not allowed in strict mode: {modifier!r}")

        return self._instantiate_block(self._scan_modifier(modifier), strict)

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
        texts = pattern.split(line)

        parts: list[LinePart] = []
        drawing_scale = 0
        for idx, text in enumerate(texts):
            if idx % 2 == 1:
                block = self.parse_block(text, strict=strict)
                parts.append(block)
                for tag in block:
                    if isinstance(tag, DrawingModeTag):
                        drawing_scale = tag.value if tag.value is not None and tag.value >= 0 else 0
                continue
            if not text and idx == 0:
                continue
            if drawing_scale > 0:
                parts.append(DrawingNode(AssShape.from_ass(text)))
            elif parse_escape_nodes:
                parts.extend(self.split_escape_nodes(text))
            else:
                parts.append(TextNode(text))

        return ParsedLine(parts=parts)
