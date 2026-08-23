import copy
from collections.abc import Sequence
from typing import ClassVar, Protocol, Self

from .constants import AssSectionHeader
from .curly import DEFAULT_TAG_PARSER, DrawingNode, TagParser
from .curly.tags import (
    BorderTag,
    BorderXTag,
    BorderYTag,
    ClipRectTag,
    ClipShapeTag,
    FontSizeAbsoluteTag,
    InverseClipRectTag,
    InverseClipShapeTag,
    MoveTag,
    OriginTag,
    PositionTag,
    ResetStyleTag,
    ShadowTag,
    ShadowXTag,
    ShadowYTag,
)
from .events import Events
from .script_info import ScriptInfo
from .styles import Styles
from .utils import detect_bytes_encoding

__all__ = [
    "Document",
]


def _split_into_sections(text: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current: list[str] | None = None
    for line in text.splitlines():
        stripped = line.lstrip(" \t")
        if stripped[:1] == "[":
            end = stripped.find("]")
            if end > 0:
                current = sections.setdefault(stripped[1:end].title(), [])
                continue
        if current is None:
            current = sections.setdefault("Unknown", [])
        current.append(line)
    return sections


class Section(Protocol):
    SECTION_NAME: ClassVar[str]

    @classmethod
    def from_lines(cls, lines: Sequence[str], strict: bool) -> Self: ...

    def to_ass(self) -> str: ...


class Document:
    def __init__(
        self,
        info: ScriptInfo | None = None,
        styles: Styles | None = None,
        events: Events | None = None,
        tag_parser: TagParser | None = None,
        section_order: Sequence[str] | None = None,
    ):
        self.info = info or ScriptInfo()
        self.styles = styles or Styles()
        self.events = events or Events()
        self.section_results: dict[str, Section] = {}
        self.unknown_sections: dict[str, list[str]] = {}
        self.tag_parser = tag_parser or DEFAULT_TAG_PARSER
        self.section_order: list[str] = list(section_order or [])

    @classmethod
    def load(
        cls,
        path: str,
        encoding: str | None = None,
        strict: bool = True,
        drop_unknown_sections: bool = True,
        extra_sections: Sequence[type[Section]] | None = None,
    ) -> Self:
        with open(path, "rb") as f:
            data = f.read()
        if encoding is None:
            encoding = detect_bytes_encoding(data[:1024]) or "utf-8-sig"
        return cls.from_string(data.decode(encoding), strict, drop_unknown_sections, extra_sections)

    @classmethod
    def from_string(
        cls,
        ass_text: str,
        strict: bool = True,
        drop_unknown_sections: bool = True,
        extra_sections: Sequence[type[Section]] | None = None,
    ) -> Self:
        doc = cls()
        doc._init_from_ass_text(ass_text, strict, drop_unknown_sections, extra_sections)
        return doc

    def _init_from_ass_text(
        self,
        ass_text: str,
        strict: bool = False,
        drop_unknown_sections: bool = True,
        extra_sections: Sequence[type[Section]] | None = None,
    ) -> None:
        if extra_sections is None:
            extra_sections = []
        extra_section_mapping = {s.SECTION_NAME: s for s in extra_sections}
        self.section_order = [s.SECTION_NAME for s in extra_sections]

        section_lines = _split_into_sections(ass_text)
        for section_name, lines in section_lines.items():
            if section_name == AssSectionHeader.SCRIPT_INFO:
                self.info = ScriptInfo.from_lines(lines, strict)
            elif section_name == AssSectionHeader.ASS_STYLES:
                self.styles = Styles.from_lines(lines, strict)
            elif section_name == AssSectionHeader.EVENTS:
                self.events = Events.from_lines(lines, strict)
            elif section := extra_section_mapping.get(section_name):
                self.section_results[section_name] = section.from_lines(lines, strict)
            elif not drop_unknown_sections:
                self.unknown_sections.setdefault(section_name, []).append("\n".join(lines).strip())

    def rename_style(self, old_name: str, new_name: str) -> None:
        self.styles.rename(old_name, new_name)
        parser = self.tag_parser or DEFAULT_TAG_PARSER
        for event in self.events:
            if event.style == old_name:
                event.style = new_name
            parsed = event.parse_tags(self, parser)
            changed = False
            for tag in parsed.get_tags(ResetStyleTag):
                if tag.value == old_name:
                    tag.value = new_name
                    changed = True
            if changed:
                event.text = parsed.to_ass()

    def resample(self, target_x: int, target_y: int) -> None:
        origin_x = self.info["PlayResX"]
        origin_y = self.info["PlayResY"]

        self.info["PlayResX"] = target_x
        self.info["PlayResY"] = target_y

        scale_x = target_x / origin_x
        scale_y = target_y / origin_y

        for style in self.styles.values():
            style.fontsize = round(style.fontsize * scale_x, 2)
            style.scale_y = round(style.scale_y * scale_y / scale_x, 2)
            style.spacing = round(style.spacing * scale_x, 2)
            style.outline = round(style.outline * scale_x, 2)
            style.shadow = round(style.shadow * scale_x, 2)
            style.margin_l = int(style.margin_l * scale_x)
            style.margin_r = int(style.margin_r * scale_x)
            style.margin_v = int(style.margin_v * scale_y)

        parser = self.tag_parser or DEFAULT_TAG_PARSER
        for event in self.events:
            event.margin_l = int(event.margin_l * scale_x)
            event.margin_r = int(event.margin_r * scale_x)
            event.margin_v = int(event.margin_v * scale_y)

            parsed = event.parse_tags(self, parser)
            modified = False
            for part in parsed.parsed:
                if isinstance(part, DrawingNode):
                    modified = True
                    part.shape.scale(scale_x, scale_y)
                elif isinstance(part, (PositionTag, OriginTag)):
                    modified = True
                    part.x = round(part.x * scale_x, 3)
                    part.y = round(part.y * scale_y, 3)
                elif isinstance(part, MoveTag):
                    modified = True
                    part.x1 = round(part.x1 * scale_x, 3)
                    part.y1 = round(part.y1 * scale_y, 3)
                    part.x2 = round(part.x2 * scale_x, 3)
                    part.y2 = round(part.y2 * scale_y, 3)
                elif isinstance(part, (ClipRectTag, InverseClipRectTag)):
                    modified = True
                    part.x1 = round(part.x1 * scale_x, 1)
                    part.y1 = round(part.y1 * scale_y, 1)
                    part.x2 = round(part.x2 * scale_x, 1)
                    part.y2 = round(part.y2 * scale_y, 1)
                elif isinstance(part, (ClipShapeTag, InverseClipShapeTag)):
                    modified = True
                    part.shape.scale(scale_x, scale_y)
                elif isinstance(part, FontSizeAbsoluteTag) and part.value is not None:
                    modified = True
                    part.value = round(part.value * scale_x, 3)
                elif isinstance(part, BorderTag) and part.value is not None:
                    modified = True
                    part.value = round(part.value * scale_x, 3)
                elif isinstance(part, BorderXTag) and part.value is not None:
                    modified = True
                    part.value = round(part.value * scale_x, 3)
                elif isinstance(part, BorderYTag) and part.value is not None:
                    modified = True
                    part.value = round(part.value * scale_y, 3)
                elif isinstance(part, ShadowTag) and part.value is not None:
                    modified = True
                    part.value = round(part.value * scale_x, 3)
                elif isinstance(part, ShadowXTag) and part.value is not None:
                    modified = True
                    part.value = round(part.value * scale_x, 3)
                elif isinstance(part, ShadowYTag) and part.value is not None:
                    modified = True
                    part.value = round(part.value * scale_y, 3)

            if modified:
                event.text = parsed.to_ass()

    def to_ass(self, section_order: Sequence[str] | None = None) -> str:
        built_in: dict[str, Section] = {
            AssSectionHeader.SCRIPT_INFO.value: self.info,
            AssSectionHeader.ASS_STYLES.value: self.styles,
            AssSectionHeader.EVENTS.value: self.events,
        }

        if section_order is None:
            section_order = [
                AssSectionHeader.SCRIPT_INFO,
                AssSectionHeader.ASS_STYLES,
                AssSectionHeader.EVENTS,
            ] + [name for name in self.section_order if name not in built_in]

        lines = []
        for name in section_order:
            if name in built_in:
                lines.append(f"[{name}]")
                lines.append(built_in[name].to_ass())
            elif name in self.section_results:
                lines.append(f"[{name}]")
                lines.append(self.section_results[name].to_ass())
            else:
                raise ValueError(f"Section {name} not found")
            lines.append("")

        return "\n".join(lines)

    def save(self, path: str, encoding: str = "utf-8-sig") -> None:
        with open(path, "w", encoding=encoding) as f:
            f.write(self.to_ass())

    def copy(self) -> Self:
        return copy.deepcopy(self)

    def __repr__(self) -> str:
        return f"Document(with {len(self.events)} events)"
