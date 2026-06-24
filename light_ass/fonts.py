import re
from dataclasses import dataclass
from typing import ClassVar, Self

from light_ass.utils.uu import uudecode, uuencode

_FONTNAME_PATTERN = re.compile(r"^\s*fontname:(.*)$", re.MULTILINE)


@dataclass
class Font:
    data: bytes

    @classmethod
    def from_raw(cls, raw: str) -> Self:
        return cls(data=uudecode(raw))

    def to_ass(self) -> str:
        return uuencode(self.data)


class Fonts:
    SECTION_NAME: ClassVar[str] = "Fonts"

    def __init__(self, fonts: dict[str, Font] | None = None) -> None:
        self.items = fonts or {}

    @classmethod
    def from_ass(cls, text: str, strict: bool = False) -> Self:
        font_dict = {}
        fontname = None
        for i, m in enumerate(_FONTNAME_PATTERN.split(text)):
            if i % 2 == 1:
                fontname = m.strip()
            elif fontname:
                font_dict[fontname] = Font.from_raw(m)
                fontname = None
        return cls(font_dict)

    def to_ass(self) -> str:
        lines = []
        for name, font in self.items.items():
            lines.append(f"fontname: {name}")
            lines.append(font.to_ass())
        return "\n".join(lines)
