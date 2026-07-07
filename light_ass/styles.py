from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass, field
from typing import Any, ClassVar, Self

from .constants import DEFAULT_STYLE_FORMAT
from .types import AssAlpha, AssColor
from .utils import Formatter, HeaderTypeParser

__all__ = [
    "Style",
    "Styles",
]


@dataclass(slots=True, kw_only=True)
class Style:
    _FIELD_PARSER: ClassVar[dict[str, tuple[str, Callable[[str], Any]]]] = {
        "name": ("name", HeaderTypeParser.parse_starred_str),
        "fontname": ("fontname", HeaderTypeParser.parse_str),
        "fontsize": ("fontsize", HeaderTypeParser.parse_float),
        "bold": ("bold", HeaderTypeParser.parse_int_bool),
        "italic": ("italic", HeaderTypeParser.parse_int_bool),
        "underline": ("underline", HeaderTypeParser.parse_int_bool),
        "strikeout": ("strike_out", HeaderTypeParser.parse_int_bool),
        "scalex": ("scale_x", HeaderTypeParser.parse_float),
        "scaley": ("scale_y", HeaderTypeParser.parse_float),
        "spacing": ("spacing", HeaderTypeParser.parse_float),
        "angle": ("angle", HeaderTypeParser.parse_float),
        "borderstyle": ("border_style", HeaderTypeParser.parse_int),
        "outline": ("outline", HeaderTypeParser.parse_float),
        "shadow": ("shadow", HeaderTypeParser.parse_float),
        "alignment": ("alignment", HeaderTypeParser.parse_int),
        "marginl": ("margin_l", HeaderTypeParser.parse_int),
        "marginr": ("margin_r", HeaderTypeParser.parse_int),
        "marginv": ("margin_v", HeaderTypeParser.parse_int),
        "encoding": ("encoding", HeaderTypeParser.parse_int),
    }

    name: str
    fontname: str = "Arial"
    fontsize: float | int = 48.0
    primary_colour: AssColor = field(default_factory=lambda: AssColor(255, 255, 255))
    primary_alpha: AssAlpha = field(default_factory=lambda: AssAlpha(0))
    secondary_colour: AssColor = field(default_factory=lambda: AssColor(255, 0, 0))
    secondary_alpha: AssAlpha = field(default_factory=lambda: AssAlpha(0))
    outline_colour: AssColor = field(default_factory=lambda: AssColor(0, 0, 0))
    outline_alpha: AssAlpha = field(default_factory=lambda: AssAlpha(0))
    back_colour: AssColor = field(default_factory=lambda: AssColor(0, 0, 0))
    back_alpha: AssAlpha = field(default_factory=lambda: AssAlpha(0))
    bold: bool = False
    italic: bool = False
    underline: bool = False
    strike_out: bool = False
    scale_x: float | int = 100.0
    scale_y: float | int = 100.0
    spacing: float | int = 0.0
    angle: float | int = 0.0
    border_style: int = 1
    outline: float | int = 2.0
    shadow: float | int = 2.0
    alignment: int = 2
    margin_l: int = 10
    margin_r: int = 10
    margin_v: int = 10
    encoding: int = 1

    @property
    def color1(self) -> AssColor:
        return self.primary_colour

    @color1.setter
    def color1(self, value: AssColor) -> None:
        self.primary_colour = value

    @property
    def alpha1(self) -> AssAlpha:
        return self.primary_alpha

    @alpha1.setter
    def alpha1(self, value: AssAlpha) -> None:
        self.primary_alpha = value

    @property
    def color2(self) -> AssColor:
        return self.secondary_colour

    @color2.setter
    def color2(self, value: AssColor) -> None:
        self.secondary_colour = value

    @property
    def alpha2(self) -> AssAlpha:
        return self.secondary_alpha

    @alpha2.setter
    def alpha2(self, value: AssAlpha) -> None:
        self.secondary_alpha = value

    @property
    def color3(self) -> AssColor:
        return self.outline_colour

    @color3.setter
    def color3(self, value: AssColor) -> None:
        self.outline_colour = value

    @property
    def alpha3(self) -> AssAlpha:
        return self.outline_alpha

    @alpha3.setter
    def alpha3(self, value: AssAlpha) -> None:
        self.outline_alpha = value

    @property
    def color4(self) -> AssColor:
        return self.back_colour

    @color4.setter
    def color4(self, value: AssColor) -> None:
        self.back_colour = value

    @property
    def alpha4(self) -> AssAlpha:
        return self.back_alpha

    @alpha4.setter
    def alpha4(self, value: AssAlpha) -> None:
        self.back_alpha = value

    @classmethod
    def from_ass(cls, line: str, format_order: tuple[str, ...] | None = None) -> Self:
        if format_order is None:
            format_order = DEFAULT_STYLE_FORMAT

        args: dict[str, Any] = {}
        _, _, line = line.partition(":")
        fields = line.split(",", len(format_order) - 1)

        for key, value in zip(format_order, fields):
            key = key.lower()
            value = value.lstrip(" \t")

            if field_ := cls._FIELD_PARSER.get(key, None):
                field_name, parser = field_
                value = parser(value)
                if field_name == "name" and not value:
                    raise ValueError(f"Invalid style name: {value!r}")
                args[field_name] = value
                continue

            # PrimaryColour, SecondaryColour, OutlineColour, BackColour
            color, alpha = HeaderTypeParser.parse_color_with_alpha(value)
            match key.lower():
                case "primarycolour":
                    args["primary_colour"] = color
                    args["primary_alpha"] = alpha
                case "secondarycolour":
                    args["secondary_colour"] = color
                    args["secondary_alpha"] = alpha
                case "outlinecolour":
                    args["outline_colour"] = color
                    args["outline_alpha"] = alpha
                case "backcolour":
                    args["back_colour"] = color
                    args["back_alpha"] = alpha
                case _:
                    raise ValueError(f"Unknown style field: {key!r}")

        return cls(**args)

    @staticmethod
    def _format_alpha_color(color: AssColor, alpha: AssAlpha) -> str:
        return f"&H{alpha.hex_value}{color.b:02X}{color.g:02X}{color.r:02X}"

    def to_ass(self) -> str:
        fontsize = Formatter.format_float(round(self.fontsize, 2))
        bold = "-1" if self.bold else "0"
        italic = "-1" if self.italic else "0"
        underline = "-1" if self.underline else "0"
        strike_out = "-1" if self.strike_out else "0"
        scale_x = Formatter.format_float(round(self.scale_x, 2))
        scale_y = Formatter.format_float(round(self.scale_y, 2))
        angle = Formatter.format_float(round(self.angle, 2))
        spacing = Formatter.format_float(round(self.spacing, 2))
        outline = Formatter.format_float(round(self.outline, 2))
        shadow = Formatter.format_float(round(self.shadow, 2))
        c1 = self._format_alpha_color(self.primary_colour, self.primary_alpha)
        c2 = self._format_alpha_color(self.secondary_colour, self.secondary_alpha)
        c3 = self._format_alpha_color(self.outline_colour, self.outline_alpha)
        c4 = self._format_alpha_color(self.back_colour, self.back_alpha)
        return (
            f"Style: {self.name},{self.fontname},{fontsize},{c1},{c2},{c3},{c4},"
            f"{bold},{italic},{underline},{strike_out},{scale_x},{scale_y},"
            f"{spacing},{angle},{self.border_style},{outline},{shadow},{self.alignment},"
            f"{self.margin_l},{self.margin_r},{self.margin_v},{self.encoding}"
        )


class Styles:
    SECTION_NAME: ClassVar[str] = "V4+ Styles"

    def __init__(self, styles: Iterable[Style] | None = None) -> None:
        self._items: dict[str, Style] = {}
        if styles:
            for style in styles:
                self._items[style.name] = style

    def __getitem__(self, key: str) -> Style:
        return self._items[key]

    def __setitem__(self, key: str, value: Style) -> None:
        value.name = key
        self._items[key] = value

    def __delitem__(self, key: str) -> None:
        del self._items[key]

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[str]:
        return iter(self._items)

    def __bool__(self) -> bool:
        return bool(self._items)

    def __contains__(self, key: object) -> bool:
        return key in self._items

    def __repr__(self) -> str:
        return f"Styles({', '.join(self._items.keys())})"

    def get(self, key: str, default: Style | None = None) -> Style | None:
        return self._items.get(key, default)

    def keys(self) -> Iterable[str]:
        return self._items.keys()

    def values(self) -> Iterable[Style]:
        return self._items.values()

    def items(self) -> Iterable[tuple[str, Style]]:
        return self._items.items()

    def set(self, style: Style) -> None:
        self[style.name] = style

    def rename(self, old_name: str, new_name: str) -> None:
        if old_name not in self._items:
            raise KeyError(f"{old_name} does not exist")
        if new_name in self._items:
            raise KeyError(f"{new_name} is already a style name")
        style = self._items.pop(old_name)
        style.name = new_name
        self._items[new_name] = style

    @classmethod
    def from_ass(cls, text: str, strict: bool = False) -> Self:
        style_list = []
        style_format = None
        for line in text.splitlines():
            if line[:7].lower() == "format:":
                if strict and style_format:
                    raise ValueError("Style Format line already declared")
                style_format = tuple(map(lambda s: s.strip(" \t").lower(), line[7:].split(",")))
            elif strict and style_format is None:
                raise ValueError("Event Format line not declared")
            else:
                style_list.append(Style.from_ass(line, style_format or DEFAULT_STYLE_FORMAT))
        return cls(style_list)

    def to_ass(self) -> str:
        return f"Format: {', '.join(DEFAULT_STYLE_FORMAT)}\n" + "\n".join(
            style.to_ass() for style in self._items.values()
        )
