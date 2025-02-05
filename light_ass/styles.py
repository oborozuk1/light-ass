from collections.abc import Iterable
from typing import Self, Literal

from .ass_types import AssColor
from .utils import validate_value

StyleKeys = Literal[
    "name",
    "fontname",
    "fontsize",
    "primary_colour",
    "secondary_colour",
    "outline_colour",
    "back_colour",
    "bold",
    "italic",
    "underline",
    "strike_out",
    "scale_x",
    "scale_y",
    "spacing",
    "angle",
    "border_style",
    "outline",
    "shadow",
    "alignment",
    "margin_l",
    "margin_r",
    "margin_v",
    "encoding",
    "color1",
    "color2",
    "color3",
    "color4",
    "align",
]


class Style(dict):
    _formats = {
        "name": str,
        "fontname": str,
        "fontsize": float,
        "primary_colour": AssColor,
        "secondary_colour": AssColor,
        "outline_colour": AssColor,
        "back_colour": AssColor,
        "bold": {"0": False, "-1": True},
        "italic": {"0": False, "-1": True},
        "underline": {"0": False, "-1": True},
        "strike_out": {"0": False, "-1": True},
        "scale_x": float,
        "scale_y": float,
        "spacing": float,
        "angle": float,
        "border_style": (1, 3, 4),  # 4 for libass
        "outline": float,
        "shadow": float,
        "alignment": (1, 2, 3, 4, 5, 6, 7, 8, 9),
        "margin_l": int,
        "margin_r": int,
        "margin_v": int,
        "encoding": int,
    }
    _alias = {
        "color1": "primary_colour",
        "color2": "secondary_colour",
        "color3": "outline_colour",
        "color4": "back_colour",
        "align": "alignment",
    }

    name: str
    fontname: str
    fontsize: float
    primary_colour: AssColor
    secondary_colour: AssColor
    outline_colour: AssColor
    back_colour: AssColor
    bold: bool
    italic: bool
    underline: bool
    strike_out: bool
    scale_x: float
    scale_y: float
    spacing: float
    angle: float
    border_style: int
    outline: float
    shadow: float
    alignment: int
    margin_l: int
    margin_r: int
    margin_v: int
    encoding: int

    color1: AssColor
    color2: AssColor
    color3: AssColor
    color4: AssColor
    align: int

    def __init__(self, from_: dict | Iterable | None = None, **kwargs):
        if from_ is not None:
            kwargs = dict(from_)
        if set(kwargs.keys()) != set(self._formats.keys()):
            raise ValueError("Keys of kwargs must equal formats")
        super().__init__({k: self.validate_value(k, v) for k, v in kwargs.items() if k != "name"})
        self._name = kwargs["name"]

    @property
    def name(self):
        return self._name

    def __getitem__(self, key: StyleKeys | str):
        if key in self._alias:
            key = self._alias[key]
        return super().__getitem__(key)

    def __setitem__(self, key: StyleKeys | str, value):
        if key in self._alias:
            key = self._alias[key]
        if key in self._formats:
            super().__setitem__(key, self.validate_value(key, value))
        else:
            raise KeyError(f"{key} is not a valid key")

    def __getattr__(self, key: str):
        return self[key]

    def __setattr__(self, key: str, value) -> None:
        if key.startswith("_"):
            super().__setattr__(key, value)
        else:
            self[key] = value

    def __repr__(self) -> str:
        return "Style({})".format(",".join(f"{key}={value}" for key, value in self.items()))

    def __str__(self) -> str:
        style_line = [self.name]
        for key, value in self.items():
            if isinstance(self._formats[key], dict):
                rev_dict = {v: k for k, v in self._formats[key].items()}
                value = rev_dict[value]
            elif type(value) is float:
                value = "{:g}".format(value)
            style_line.append(str(value))
        return f"Style: {','.join(style_line)}"

    @staticmethod
    def validate_value(key, value):
        if key in Style._alias:
            key = Style._alias[key]
        try:
            return validate_value(Style._formats[key], value)
        except ValueError:
            raise ValueError(f"Invalid value for {key}: {value}")


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
