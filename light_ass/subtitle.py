import copy
import pathlib
from collections import defaultdict

from .constants import SECTION_PATTERN, AssSectionHeader, DEFAULT_STYLES_FORMAT, DEFAULT_EVENTS_FORMAT
from .events import Dialog, Events
from .script_info import ScriptInfo
from .styles import Styles, Style
from .tag_parser import join_tags
from .utils import to_snake_case, detect_file_encoding

__all__ = [
    "Subtitle",
    "load",
    "from_string",
]


class Subtitle:
    def __init__(self):
        self.messages = []
        self.info = ScriptInfo()
        self.styles = Styles()
        self.events = Events()
        self.other_sections = defaultdict(list)
        self.path: pathlib.Path | None = None

    @classmethod
    def load(cls, path: pathlib.Path | str, encoding: str | None = None, strict: bool = True,
             drop_unknown_sections: bool = True) -> "Subtitle":
        """
        Load subtitle from file.
        :param path: Where the subtitle file is located.
        :param encoding: The encoding of the file. If None, the encoding will be detected.
        :param strict: If false, ignore warnings.
        :param drop_unknown_sections: If false, store unknown sections as is.
        :return: A Subtitle object.
        """
        if encoding is None:
            encoding = detect_file_encoding(str(path)) or "utf-8-sig"
        doc = cls()
        doc.path = pathlib.Path(path)
        with open(path, "r", encoding=encoding) as f:
            doc._init_from_ass_text(f.read(), strict, drop_unknown_sections)
        return doc

    @classmethod
    def from_string(cls, ass_text: str, strict: bool = True, drop_unknown_sections: bool = True) -> "Subtitle":
        """
        Load subtitle from an ASS string.
        :param ass_text: An ASS formatted string.
        :param strict: If false, ignore warnings.
        :param drop_unknown_sections: If false, store unknown sections as is.
        :return: A Subtitle object.
        """
        doc = cls()
        doc._init_from_ass_text(ass_text, strict, drop_unknown_sections)
        return doc

    def _init_from_ass_text(self, ass_text: str, strict: bool, drop_unknown_sections: bool) -> None:
        def process_info_line(line: str):
            if line.startswith((";", "!:")):
                line = line.removeprefix(";").removeprefix("!:").strip()
                self.messages.append(line)
            else:
                key, _, value = map(str.strip, line.partition(":"))
                self.info.set(key, value)

        def parse_format_line(line: str, default):
            if strict and formats.get(section):
                raise ValueError(f"{section} Format line already declared")
            _, _, format_ = line.partition(":")
            formats[section] = map(str.strip, format_.split(",", len(default)))
            formats[section] = list(map(to_snake_case, formats[section]))

        def check_format():
            if not formats.get(section):
                if strict:
                    raise ValueError(f"{section} Format line not declared")
                else:
                    return False
            return True

        def process_styles_line(line: str):
            if line.startswith("Format:"):
                parse_format_line(line, DEFAULT_STYLES_FORMAT)
            elif line.startswith("Style:"):
                if not check_format():
                    formats[section] = DEFAULT_STYLES_FORMAT
                self.styles.set(Style.from_ass_line(line, formats[section]))
            elif strict:
                raise ValueError(f"Invalid Style line: {line}")

        def process_events_line(line: str):
            if line.startswith("Format:"):
                parse_format_line(line, DEFAULT_EVENTS_FORMAT)
                if formats[section][-1] != "text":
                    raise ValueError("Text must be the last column in Event format.")
            elif line.startswith(("Dialogue:", "Comment:")):
                if not check_format():
                    formats[section] = DEFAULT_EVENTS_FORMAT
                self.events.append(Dialog.from_ass_line(line, formats[section]))
            elif strict:
                raise ValueError(f"Invalid Event line: {line}")

        def process_other_sections_line(line: str):
            if not drop_unknown_sections:
                self.other_sections[section].append(line)

        handlers = {
            AssSectionHeader.SCRIPT_INFO: process_info_line,
            AssSectionHeader.ASS_STYLE: process_styles_line,
            AssSectionHeader.EVENTS: process_events_line,
        }
        section = ""
        formats = {}
        for line in ass_text.splitlines():
            line = line.lstrip(" ")
            if not line:
                continue
            if match := SECTION_PATTERN.match(line):
                section = match.group(1).title()
            else:
                handlers.get(section, process_other_sections_line)(line)

        default_info = {
            "ScaledBorderAndShadow": True,
            "YCbCr Matrix": "None",
            "PlayResX": self.info.get("LayoutResX", None) or 1920,
            "PlayResY": self.info.get("LayoutResY", None) or 1080,
            "LayoutResX": self.info.get("PlayResX", None) or 1920,
            "LayoutResY": self.info.get("PlayResY", None) or 1080,
        }

        self.info |= default_info | self.info

    def rename_style(self, old_name: str, new_name: str):
        """
        Rename a style.
        :param old_name: The name of the style to rename.
        :param new_name: The new name of the style.
        :return:
        """
        self.styles.rename(old_name, new_name)
        for event in self.events:
            if event.style == old_name:
                event.style = new_name
            tags = event.parse_tags()
            flag = False
            for tag in tags:
                if tag.name == "r" and tag.args == (old_name,):
                    tag.args = (new_name,)
                    flag = True
            if flag:
                event.text = join_tags(tags)

    def resample(self, target_x: int, target_y: int) -> None:
        """
        Resample the subtitle to the target resolution.
        :param target_x: The target width.
        :param target_y: The target height.
        :return: None
        """
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

        for event in self.events:
            event.margin_l = int(event.margin_l * scale_x)
            event.margin_r = int(event.margin_r * scale_x)
            event.margin_v = int(event.margin_v * scale_y)

            tags = event.parse_tags()
            for tag in tags:
                if not tag.valid:
                    continue

                if tag.name == "pos" or tag.name == "org":
                    tag.args = (round(tag.args[0] * scale_x, 3), round(tag.args[1] * scale_y, 2))
                elif tag.name == "move":
                    if len(tag.args) == 4:
                       tag.args = (round(tag.args[0] * scale_x, 3), round(tag.args[1] * scale_y, 3),
                                   round(tag.args[2] * scale_x, 3), round(tag.args[3] * scale_y, 3))
                    elif len(tag.args) == 6:
                       tag.args = (round(tag.args[0] * scale_x, 3), round(tag.args[1] * scale_y, 3),
                                   round(tag.args[2] * scale_x, 3), round(tag.args[3] * scale_y, 3),
                                   tag.args[4], tag.args[5])
                elif tag.name == "clip" or tag.name == "iclip":
                    if len(tag.args) == 4:
                        tag.args = (int(tag.args[0] * scale_x), int(tag.args[1] * scale_y),
                                    int(tag.args[2] * scale_x), int(tag.args[3] * scale_y))
                    else:
                        tag.args[0].scale(scale_x * 100, scale_y * 100).round(3)
                elif tag.name == "fs" and tag.args and isinstance(tag.args[0], (float, int)):
                    tag.args = (round(tag.args[0] * scale_x, 3),)
                elif tag.name == "bord" and tag.args and isinstance(tag.args[0], (float, int)):
                    tag.args = (round(tag.args[0] * scale_x, 3),)
                elif tag.name == "xbord" and tag.args and isinstance(tag.args[0], (float, int)):
                    tag.args = (round(tag.args[0] * scale_x, 3),)
                elif tag.name == "ybord" and tag.args and isinstance(tag.args[0], (float, int)):
                    tag.args = (round(tag.args[0] * scale_y, 3),)
                elif tag.name == "shad" and tag.args and isinstance(tag.args[0], (float, int)):
                    tag.args = (round(tag.args[0] * scale_x, 3),)
                elif tag.name == "xshad" and tag.args and isinstance(tag.args[0], (float, int)):
                    tag.args = (round(tag.args[0] * scale_x, 3),)
                elif tag.name == "yshad" and tag.args and isinstance(tag.args[0], (float, int)):
                    tag.args = (round(tag.args[0] * scale_y, 3),)

            event.text = join_tags(tags)

    def to_string(self) -> str:
        """
        Convert the Subtitle object to an ASS formatted string.
        :return: An ASS formatted string.
        """
        lines = ["[Script Info]"]
        if self.messages:
            lines.append("\n".join(f"; {message}" for message in self.messages))

        styles = "\n".join(style.to_string() for style in self.styles.values())
        lines += [str(self.info), "\n[V4+ Styles]",
                  "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
                  "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, "
                  "Shadow, Alignment, MarginL, MarginR, MarginV, Encoding", styles, "\n[Events]",
                  "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]

        for event in self.events:
            lines.append(event.to_string())

        for name, content in self.other_sections.items():
            lines.append(f"\n[{name}]")
            lines.extend(content)

        return "\n".join(lines)

    def save(self, path: pathlib.Path | str, encoding: str = "utf-8-sig") -> None:
        """
        Save the Subtitle object to the path with the given encoding.
        :param path: The path to save the subtitle to.
        :param encoding: The encoding to use when saving the file.
        :return: None
        """
        with open(path, "w", encoding=encoding) as f:
            f.write(self.to_string())

    def copy(self) -> "Subtitle":
        """
        Create a deep copy of the Subtitle object.
        :return: A deep copy of the Subtitle object.
        """
        return copy.deepcopy(self)

    def __repr__(self) -> str:
        return f"Subtitle(with {len(self.events)} events)"



load = Subtitle.load
from_string = Subtitle.from_string
