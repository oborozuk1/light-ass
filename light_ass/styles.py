from dataclasses import dataclass, field
from typing import Self, Iterable

from .ass_types import AssColor
from .constants import DEFAULT_STYLES_FORMAT
from .utils import to_snake_case

__all__ = [
    "Style",
    "Styles",
]


@dataclass(kw_only=True)
class Style:
    name: str
    fontname: str = "Arial"
    fontsize: float | int = 48.0
    primary_colour: AssColor = field(default_factory=lambda: AssColor(255, 255, 255))
    secondary_colour: AssColor = field(default_factory=lambda: AssColor(255, 0, 0))
    outline_colour: AssColor = field(default_factory=lambda: AssColor(0, 0, 0))
    back_colour: AssColor = field(default_factory=lambda: AssColor(0, 0, 0))
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
    def color2(self) -> AssColor:
        return self.secondary_colour

    @color2.setter
    def color2(self, value: AssColor) -> None:
        self.secondary_colour = value

    @property
    def color3(self) -> AssColor:
        return self.outline_colour

    @color3.setter
    def color3(self, value: AssColor) -> None:
        self.outline_colour = value

    @property
    def color4(self) -> AssColor:
        return self.back_colour

    @color4.setter
    def color4(self, value: AssColor) -> None:
        self.back_colour = value

    @property
    def align(self) -> int:
        return self.alignment

    def __repr__(self) -> str:
        return f"Style(name={self.name})"

    @classmethod
    def from_ass_line(cls, line: str, format_order: Iterable[str] | None = None):
        if format_order is None:
            format_order = DEFAULT_STYLES_FORMAT

        length = sum(1 for _ in format_order)

        kwargs = {}
        fields = line.removeprefix("Style:").split(",", length - 1)
        for key, value in zip(format_order, fields):
            key = to_snake_case(key)
            value = value.strip()
            if key in ("bold", "italic", "underline", "strike_out"):
                value = value == "-1"
            elif key in ("margin_l", "margin_r", "margin_v"):
                value = int(value)
            elif key in ("fontsize", "scale_x", "scale_y", "spacing", "angle", "outline", "shadow"):
                value = float(value)
            kwargs[key] = value

        return cls(**kwargs)

    def to_string(self) -> str:
        fontsize = int(self.fontsize) if self.fontsize.is_integer() else self.fontsize
        bold = -1 if self.bold else 0
        italic = -1 if self.italic else 0
        underline = -1 if self.underline else 0
        strike_out = -1 if self.strike_out else 0
        scale_x = int(self.scale_x) if self.scale_x.is_integer() else self.scale_x
        scale_y = int(self.scale_y) if self.scale_y.is_integer() else self.scale_y
        angle = int(self.angle) if self.angle.is_integer() else self.angle
        spacing = int(self.spacing) if self.spacing.is_integer() else self.spacing
        outline = int(self.outline) if self.outline.is_integer() else self.outline
        shadow = int(self.shadow) if self.shadow.is_integer() else self.shadow
        return (f"Style: {self.name},{self.fontname},{fontsize},{self.primary_colour},{self.secondary_colour},"
                f"{self.outline_colour},{self.back_colour},{bold},{italic},{underline},{strike_out},{scale_x},{scale_y},"
                f"{spacing},{angle},{self.border_style},{outline},{shadow},{self.alignment},"
                f"{self.margin_l},{self.margin_r},{self.margin_v},{self.encoding}")


class Styles(dict[str, Style]):
    def __init__(self, from_: Self | dict[str, Style] | None = None):
        if from_ is None:
            super().__init__()
        else:
            super().__init__(from_)

    def __setitem__(self, key, value):
        if isinstance(value, Style):
            value._name = key
            super().__setitem__(key, value)
        else:
            raise TypeError("value must be a Style")

    def __repr__(self):
        return f"Styles({", ".join(self.keys())})"

    def __str__(self):
        return "\n".join((str(style) for style in self.values()))

    def set(self, style: Style) -> None:
        """
        Add a style to the collection. If the style name is already in use, it will be replaced.
        :param style: The style to add.
        :return: None
        """
        self[style.name] = style

    def rename(self, old_name: str, new_name: str) -> None:
        """
        Rename a style. Note that you should use Subtitle.rename_style if you want to rename a style in a Subtitle object.
        :param old_name: The name of the style to rename.
        :param new_name: The new name of the style.
        :return: None
        """
        if old_name not in self:
            raise KeyError(f"{old_name} does not exist")
        if new_name in self:
            raise KeyError(f"{new_name} is already a style name")
        style = self.pop(old_name)
        style._name = new_name
        self[new_name] = style
