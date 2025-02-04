import re


class AssSectionHeader:
    SCRIPT_INFO = "Script Info"
    ASS_STYLE = "V4+ Styles"
    EVENTS = "Events"
    # AEGISUB_PROJECT = "Aegisub Project Garbage"
    # AEGISUB_EXTRADATA = "Aegisub Extradata"
    # FONTS = "Fonts"
    # GRAPHICS = "Graphics"


DEFAULT_STYLES_FORMAT = (
    "Name", "Fontname", "Fontsize", "PrimaryColour", "SecondaryColour", "OutlineColour", "BackColour",
    "Bold", "Italic", "Underline", "StrikeOut", "ScaleX", "ScaleY", "Spacing", "Angle", "BorderStyle",
    "Outline", "Shadow", "Alignment", "MarginL", "MarginR", "MarginV", "Encoding",
)

DEFAULT_EVENTS_FORMAT = ("Layer", "Start", "End", "Style", "Name", "MarginL", "MarginR", "MarginV", "Effect", "Text")

SECTION_PATTERN = re.compile(r"^\s*\[([^]]+)]\s*")

OVERRIDE_BLOCK_PATTERN = re.compile(r"(?<!\\){([^}]*)}")
