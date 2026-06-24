import re
from dataclasses import dataclass
from typing import ClassVar, Self

_FONTNAME_PATTERN = re.compile(r"^\s*fontname:(.*)$", re.MULTILINE)


def uudecode(s: str) -> bytes:
    values = []
    for ch in s:
        if ch == "\n" or ch == "\r":
            continue
        values.append(ord(ch) - 33)

    result = bytearray()
    for i in range(0, len(values), 4):
        group = values[i : i + 4]
        src = group + [0] * (4 - len(group))
        cnt = len(group)

        if cnt > 1:
            result.append((src[0] << 2) | (src[1] >> 4))
        if cnt > 2:
            result.append(((src[1] & 0x0F) << 4) | (src[2] >> 2))
        if cnt > 3:
            result.append(((src[2] & 0x03) << 6) | (src[3]))

    return bytes(result)


def uuencode(data: bytes, insert_linebreaks: bool = True) -> str:
    size = len(data)
    result = []
    written = 0

    for pos in range(0, size, 3):
        chunk = data[pos : pos + 3]
        src = chunk + b"\x00" * (3 - len(chunk))

        dst = [
            src[0] >> 2,
            ((src[0] & 0x03) << 4) | ((src[1] & 0xF0) >> 4),
            ((src[1] & 0x0F) << 2) | ((src[2] & 0xC0) >> 6),
            src[2] & 0x3F,
        ]

        valid = min(size - pos + 1, 4)

        for i in range(valid):
            result.append(chr(dst[i] + 33))
            if insert_linebreaks:
                written += 1
                if written == 80 and pos + 3 < size:
                    written = 0
                    result.append("\r\n")

    return "".join(result)


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
