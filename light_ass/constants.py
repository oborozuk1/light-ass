import re
from enum import StrEnum

__all__ = [
    "AssSectionHeader",
    "DEFAULT_STYLE_FORMAT",
    "DEFAULT_EVENT_FORMAT",
    "OVERRIDE_BLOCK_PATTERN",
]


class YCbCrMatrix(StrEnum):
    NONE = "NONE"
    BT601_TV = "TV.601"
    BT601_PC = "PC.601"
    BT709_TV = "TV.709"
    BT709_PC = "PC.709"
    SMPTE240M_TV = "TV.240M"
    SMPTE240M_PC = "PC.240M"
    FCC_TV = "TV.FCC"
    FCC_PC = "PC.FCC"


class AssSectionHeader(StrEnum):
    SCRIPT_INFO = "Script Info"
    ASS_STYLES = "V4+ Styles"
    EVENTS = "Events"
    AEGISUB_PROJECT_GARBAGE = "Aegisub Project Garbage"
    AEGISUB_EXTRADATA = "Aegisub Extradata"
    FONTS = "Fonts"
    GRAPHICS = "Graphics"


DEFAULT_STYLE_FORMAT = (
    "Name",
    "Fontname",
    "Fontsize",
    "PrimaryColour",
    "SecondaryColour",
    "OutlineColour",
    "BackColour",
    "Bold",
    "Italic",
    "Underline",
    "StrikeOut",
    "ScaleX",
    "ScaleY",
    "Spacing",
    "Angle",
    "BorderStyle",
    "Outline",
    "Shadow",
    "Alignment",
    "MarginL",
    "MarginR",
    "MarginV",
    "Encoding",
)

DEFAULT_EVENT_FORMAT = (
    "Layer",
    "Start",
    "End",
    "Style",
    "Name",
    "MarginL",
    "MarginR",
    "MarginV",
    "Effect",
    "Text",
)

OVERRIDE_BLOCK_PATTERN = re.compile(r"(?<!\\){(.*?)}")
