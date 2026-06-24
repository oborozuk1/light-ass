from collections.abc import Callable, Iterator
from typing import Any, ClassVar, Literal, Self

from .utils import HeaderTypeParser

__all__ = [
    "ScriptInfo",
]


ScriptInfoKeys = Literal[
    "Title",
    "Original Script",
    "Original Translation",
    "Original Editing",
    "Original Timing",
    "Synch Point",
    "Script Updated By",
    "ScriptType",
    "Update Details",
    "PlayResX",
    "PlayResY",
    "PlayDepth",
    "ScaledBorderAndShadow",
    "WrapStyle",
    "YCbCr Matrix",
    "Collisions",
    "Timer",
    "LayoutResX",
    "LayoutResY",
    # libass extensions
    "Kerning",
    "Language",
]


class ScriptInfo:
    SECTION_NAME: ClassVar[str] = "Script Info"

    _FIELD_PARSER: ClassVar[dict[str, tuple[str, Callable[[str], Any]]]] = {
        "PLAYRESX": ("PlayResX", HeaderTypeParser.parse_int),
        "PLAYRESY": ("PlayResY", HeaderTypeParser.parse_int),
        "LAYOUTRESX": ("LayoutResX", HeaderTypeParser.parse_int),
        "LAYOUTRESY": ("LayoutResY", HeaderTypeParser.parse_int),
        "TIMER": ("Timer", HeaderTypeParser.parse_float),
        "WRAPSTYLE": ("WrapStyle", HeaderTypeParser.parse_int),
        "SCALEDBORDERANDSHADOW": ("ScaledBorderAndShadow", HeaderTypeParser.parse_bool),
        "KERNING": ("Kerning", HeaderTypeParser.parse_bool),
        "YCBCR MATRIX": ("YCbCr Matrix", HeaderTypeParser.parse_ycbcr_matrix),
    }

    def __init__(
        self, info: Self | dict[str, Any] | None = None, messages: list[str] | None = None
    ) -> None:
        self._items: dict[str, Any] = {}
        self.messages: list[str] = messages or []
        if isinstance(info, ScriptInfo):
            self._items = dict(info._items)
        elif isinstance(info, dict):
            self._init_from_dict(info, messages)

    def __getitem__(self, key: ScriptInfoKeys | str) -> Any:
        return self._items[key]

    def __setitem__(self, key: ScriptInfoKeys | str, value: Any) -> None:
        self._items[key] = value

    def __delitem__(self, key: ScriptInfoKeys | str) -> None:
        del self._items[key]

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[str]:
        return iter(self._items)

    def __bool__(self) -> bool:
        return bool(self._items)

    def __contains__(self, key: object) -> bool:
        return key in self._items

    def __ior__(self, other: dict[str, Any]) -> Self:
        for key, value in other.items():
            self._items[key] = value
        return self

    def __or__(self, other: dict[str, Any]) -> dict[str, Any]:
        result = dict(self._items)
        result.update(other)
        return result

    def __ror__(self, other: dict[str, Any]) -> dict[str, Any]:
        result = dict(other)
        result.update(self._items)
        return result

    def __repr__(self) -> str:
        return f"ScriptInfo({self._items!r})"

    def get(self, key: str, default: Any = None) -> Any:
        return self._items.get(key, default)

    def keys(self) -> list[str]:
        return list(self._items.keys())

    def values(self) -> list[Any]:
        return list(self._items.values())

    def items(self) -> list[tuple[str, Any]]:
        return list(self._items.items())

    def set(self, key: ScriptInfoKeys | str, value: Any) -> None:
        if value is None:
            self._items.pop(key, None)
        elif key.upper() in self._FIELD_PARSER and isinstance(value, str):
            _, parser = self._FIELD_PARSER[key.upper()]
            self._items[key] = parser(value)
        else:
            self._items[key] = value

    @classmethod
    def from_ass(cls, text: str, strict: bool = False) -> Self:
        info = {}
        messages = []
        for line in text.splitlines():
            if line.startswith(";"):
                messages.append(line[1:].strip())
            elif line.startswith("!:"):
                messages.append(line[2:].strip())
            else:
                key, _, value = map(str.strip, line.partition(":"))
                info[key] = value
        return cls.from_dict(info, messages)

    @classmethod
    def from_dict(cls, dic: dict[str, Any], messages: list[str] | None = None) -> Self:
        info = cls()
        info._init_from_dict(dic, messages)
        return info

    def _init_from_dict(self, d: dict[str, Any], messages: list[str] | None = None) -> None:
        for key, value in d.items():
            self.set(key, value)
        self.messages = messages or []

    def to_ass(self) -> str:
        parts = []
        for key, value in self._items.items():
            if isinstance(value, bool):
                value = "yes" if value else "no"
            parts.append(f"{key}: {value}")
        return "\n".join(parts)
