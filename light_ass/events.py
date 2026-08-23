from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator, Sequence
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, ClassVar, Self, overload

from .constants import DEFAULT_EVENT_FORMAT, OVERRIDE_BLOCK_PATTERN
from .curly import DEFAULT_TAG_PARSER
from .types import AssTime
from .utils import HeaderTypeParser

DEFAULT_EVENT_FORMAT_LOWER = tuple(s.lower() for s in DEFAULT_EVENT_FORMAT)

if TYPE_CHECKING:
    from .curly import TagParser
    from .document import Document
    from .parsed_event import ParsedDialog

__all__ = [
    "Dialog",
    "Events",
]


@dataclass(slots=True, kw_only=True)
class Dialog:
    _FIELD_PARSER: ClassVar[dict[str, tuple[str, Callable[[str], Any]]]] = {
        "layer": ("layer", HeaderTypeParser.parse_int),
        "start": ("start", HeaderTypeParser.parse_time),
        "end": ("end", HeaderTypeParser.parse_time),
        "style": ("style", HeaderTypeParser.parse_starred_str),
        "name": ("name", HeaderTypeParser.parse_str),
        "marginl": ("margin_l", HeaderTypeParser.parse_int),
        "marginr": ("margin_r", HeaderTypeParser.parse_int),
        "marginv": ("margin_v", HeaderTypeParser.parse_int),
        "effect": ("effect", HeaderTypeParser.parse_str),
        "text": ("text", HeaderTypeParser.parse_str),
    }

    text: str
    comment: bool = False
    layer: int = 0
    start: AssTime = field(default_factory=lambda: AssTime(0))
    end: AssTime = field(default_factory=lambda: AssTime(0))
    style: str = "Default"
    name: str = ""
    margin_l: int = 0
    margin_r: int = 0
    margin_v: int = 0
    effect: str = ""

    @property
    def duration(self) -> AssTime:
        return self.end - self.start

    @property
    def text_stripped(self) -> str:
        return OVERRIDE_BLOCK_PATTERN.sub("", self.text)

    @classmethod
    def from_ass(cls, line: str, format_order: tuple[str, ...] | None = None) -> Self:
        if format_order is None or format_order == DEFAULT_EVENT_FORMAT_LOWER:
            return cls._from_ass_default(line)

        if format_order[-1].lower() != "text":
            raise ValueError(
                f"Invalid event format: {format_order!r}. \nThe last field must be 'Text'"
            )

        args: dict[str, Any] = {"comment": line[:8].lower() == "comment:"}
        _, _, line = line.partition(":")
        fields = line.split(",", len(format_order) - 1)

        for key, value in zip(format_order, fields):
            key = key.lower()
            value = value.lstrip(" \t")

            if field_ := cls._FIELD_PARSER.get(key, None):
                field_name, parser = field_
                args[field_name] = parser(value)

        return cls(**args)

    @classmethod
    def _from_ass_default(cls, line: str) -> Self:
        comment = line[0] in "Cc"
        _, _, line = line.partition(":")
        fields = line.split(",", 9)
        layer, start, end, style, name, margin_l, margin_r, margin_v, effect, text = fields
        return cls(
            text=text.lstrip(" \t"),
            comment=comment,
            layer=HeaderTypeParser.parse_int(layer),
            start=AssTime.parse(start),
            end=AssTime.parse(end),
            style=style.lstrip(" \t").lstrip("*"),
            name=name.lstrip(" \t"),
            margin_l=HeaderTypeParser.parse_int(margin_l),
            margin_r=HeaderTypeParser.parse_int(margin_r),
            margin_v=HeaderTypeParser.parse_int(margin_v),
            effect=effect.lstrip(" \t"),
        )

    def to_ass(self) -> str:
        type_ = "Dialogue" if not self.comment else "Comment"
        return (
            f"{type_}: {self.layer},{self.start},{self.end},{self.style},{self.name},"
            f"{self.margin_l},{self.margin_r},{self.margin_v},{self.effect},{self.text}"
        )

    def shift(self, ms: int) -> None:
        self.start += ms
        self.end += ms

    def parse_tags(
        self,
        doc: Document,
        parser: TagParser | None = None,
        strict: bool | None = None,
        escape_brace: bool | None = None,
        parse_escape_nodes: bool = False,
    ) -> ParsedDialog:
        from .parsed_event import ParsedDialog

        if parser is None:
            parser = DEFAULT_TAG_PARSER
        parsed = parser.parse(self.text, strict, escape_brace, parse_escape_nodes)
        return ParsedDialog(doc=doc, event=self, parsed=parsed)


class Events:
    SECTION_NAME: ClassVar[str] = "Events"

    def __init__(self, events: list[Dialog] | None = None) -> None:
        if events is None:
            events = []
        self._items: list[Dialog] = events

    @overload
    def __getitem__(self, index: int) -> Dialog: ...
    @overload
    def __getitem__(self, index: slice) -> list[Dialog]: ...
    def __getitem__(self, index: int | slice) -> Dialog | list[Dialog]:
        return self._items[index]

    @overload
    def __setitem__(self, index: int, value: Dialog) -> None: ...

    @overload
    def __setitem__(self, index: slice, value: Sequence[Dialog]) -> None: ...

    def __setitem__(self, index: int | slice, value: Dialog | Sequence[Dialog]) -> None:
        self._items[index] = value  # type: ignore[assignment, index]

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[Dialog]:
        return iter(self._items)

    def __bool__(self) -> bool:
        return bool(self._items)

    def __repr__(self) -> str:
        return f"Events({len(self._items)} dialogs)"

    def append(self, dialog: Dialog) -> None:
        self._items.append(dialog)

    def extend(self, dialogs: Sequence[Dialog]) -> None:
        for dialog in dialogs:
            self.append(dialog)

    def pop(self, index: int | Iterable[int] = -1) -> Dialog | list[Dialog]:
        if isinstance(index, int):
            return self._items.pop(index)
        result = []
        for i in sorted(index, reverse=True):
            result.append(self._items.pop(i))
        return list(reversed(result))

    def sort(self, *, key: Callable[[Dialog], Any] | None = None, reverse: bool = False) -> None:
        if key is None:

            def key(x: Dialog) -> Any:
                return x.start

        self._items.sort(key=key, reverse=reverse)

    def shift(self, ms: int, range_: Sequence[int] | None = None) -> None:
        if range_ is None:
            range_ = range(0, len(self._items))
        for i in range_:
            self._items[i].shift(ms)

    @classmethod
    def from_lines(cls, lines: Sequence[str], strict: bool = False) -> Self:
        dialog_list = []
        event_format = None
        use_fast = True
        for line in lines:
            if not line or line.isspace():
                continue
            if line[:7].lower() == "format:":
                if strict and event_format:
                    raise ValueError("Event Format line already declared")
                event_format = tuple(map(lambda s: s.strip(" \t").lower(), line[7:].split(",")))
                use_fast = event_format == DEFAULT_EVENT_FORMAT_LOWER
            elif strict and event_format is None:
                raise ValueError("Event Format line not declared")
            elif line[:9].lower() != "dialogue:" and line[:8].lower() != "comment:":
                if strict:
                    raise ValueError(f"Invalid event line: {line!r}")
            elif use_fast:
                dialog_list.append(Dialog._from_ass_default(line))
            else:
                dialog_list.append(Dialog.from_ass(line, event_format))
        return cls(dialog_list)

    @classmethod
    def from_ass(cls, text: str, strict: bool = False) -> Self:
        return cls.from_lines(text.splitlines(), strict)

    def to_ass(self) -> str:
        return f"Format: {', '.join(DEFAULT_EVENT_FORMAT)}\n" + "\n".join(
            dialog.to_ass() for dialog in self._items
        )
