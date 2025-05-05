import re
from typing import Sequence, Any

from .ass_types import AssColor, AssAlpha, AssDrawing
from .constants import OVERRIDE_BLOCK_PATTERN
from .utils import parse_int32, parse_positive_int32, parse_float, parse_positive_float, \
    parse_ass_color, parse_ass_alpha

__all__ = [
    "Tag",
    "parse_tags",
    "join_tags",
    "is_simple_tag",
    "is_complex_tag",
    "is_line_tag",
    "is_unknown_tag"
]

_int = parse_int32
_positive_int = parse_positive_int32
_float = parse_float
_positive_float = parse_positive_float
_ass_color = parse_ass_color
_ass_alpha = parse_ass_alpha


class FallbackError(Exception):
    pass


class InvalidArgError(Exception):
    pass


def is_simple_tag(name: str) -> bool:
    """
    Check if the tag is a simple tag.
    :param name: The name of the tag.
    :return: True if the tag is a simple tag, False otherwise.
    """
    simple_tags = (
        "xbord", "ybord", "xshad", "yshad", "fax", "fay", "blur", "fscx", "fscy", "fsc", "fsp", "fs", "bord", "frx",
        "fry", "frz", "fr", "fn", "alpha", "an", "a", "c", "1c", "2c", "3c", "4c", "1a", "2a", "3a", "4a", "r", "be",
        "b", "i", "kt", "kf", "K", "ko", "k", "shad", "s", "u", "pbo", "p", "q", "fe"
    )
    return name in simple_tags


def is_complex_tag(name: str) -> bool:
    """
    Check if the tag is a complex tag.
    :param name: The name of the tag.
    :return: True if the tag is a complex tag, False otherwise.
    """
    complex_tags = ("t", "clip", "iclip", "move", "fade", "fad", "pos", "org")
    return name in complex_tags


def is_line_tag(name: str) -> bool:
    """
    Check if the tag is a line tag.
    :param name: The name of the tag.
    :return: True if the tag is a line tag, False otherwise.
    """
    line_tags = ("clip", "iclip", "move", "fade", "fad", "pos", "org", "an", "a")
    return name in line_tags


def is_special_tag(name: str) -> bool:
    """
    Check if the tag is a special tag. Special tags are Drawing, Text, and Comment.
    :param name: The name of the tag.
    return: True if the tag is a special tag, False otherwise.
    """
    special_tags = ("Comment", "Drawing", "Text")
    return name in special_tags


def is_unknown_tag(name: str) -> bool:
    """
    Check if the tag is an unknown tag.
    :param name: The name of the tag.
    :return: True if the tag is an unknown tag, False otherwise.
    """
    return not is_special_tag(name) and name not in tag_args


def is_nestable_tag(name: str) -> bool:
    """
    Check if the tag is a nestable tag.
    :param name: The name of the tag.
    :return: True if the tag is a nestable tag, False otherwise.
    """
    nestable_tags = (
        "xbord", "ybord", "xshad", "yshad", "fax", "fay", "blur", "fscx", "fscy", "fsp", "fs", "bord", "frx",
        "fry", "frz", "fr", "alpha", "c", "1c", "2c", "3c", "4c", "1a", "2a", "3a", "4a", "be", "shad", "clip", "iclip"
    )
    return name in nestable_tags


def format_arg(arg) -> str:
    """
    Format an argument.
    :param arg: The argument to format.
    :return: The formatted argument.
    """
    match arg:
        case float():
            arg = f"{arg:g}"
        case list():
            return "".join(map(lambda t: t.to_string(), arg))
        case AssAlpha():
            arg = arg.format()
        case AssColor():
            arg = arg.format("&H{B}{G}{R}&")
        case _:
            arg = str(arg).strip()
    return arg


class Tag:
    def __init__(self, name: str, args, valid: bool | None = None):
        self.name = name
        self.args, self.valid = self.validate_args(name, args)
        if valid is not None:
            self.valid = valid

    def __eq__(self, other):
        return self.name == other.name and self.args == other.args

    def __repr__(self):
        return f"Tag(name={self.name}, with {len(self.args)} {"arg" if len(self.args) == 1 else "args"})"

    def __str__(self):
        return self.to_string()

    def to_string(self) -> str:
        """
        Convert the tag to a string.
        :return: The string representation of the tag.
        """
        if self.is_special_tag:
            return self.args[0]
        if len(self.args) == 0:
            return f"\\{self.name}"
        elif self.is_simple_tag and len(self.args) == 1:
            return f"\\{self.name}{format_arg(self.args[0])}"
        else:
            return f"\\{self.name}({','.join(map(lambda s: format_arg(s), self.args))})"

    @property
    def is_simple_tag(self) -> bool:
        """
        Check if the tag is a simple tag.
        :return: True if the tag is a simple tag, False otherwise.
        """
        return is_simple_tag(self.name)

    @property
    def is_complex_tag(self) -> bool:
        """
        Check if the tag is a complex tag.
        :return: True if the tag is a complex tag, False otherwise.
        """
        return is_complex_tag(self.name)

    @property
    def is_line_tag(self) -> bool:
        """
        Check if the tag is a line tag.
        :return: True if the tag is a line tag, False otherwise.
        """
        return is_line_tag(self.name)

    @property
    def is_special_tag(self) -> bool:
        """
        Check if the tag is a special tag.
        :return: True if the tag is a special tag, False otherwise.
        """
        return is_special_tag(self.name)

    @property
    def is_unknown_tag(self) -> bool:
        """
        Check if the tag is an unknown tag.
        :return: True if the tag is an unknown tag, False otherwise.
        """
        return is_unknown_tag(self.name)

    @staticmethod
    def _validate_args(name: str, args: Sequence[str]) -> tuple[tuple, bool]:
        args = tuple(args)
        validators = None
        for typ in tag_args[name]:
            if len(args) == len(typ):
                validators = typ
                break
        if validators is None:
            return args, False
        try:
            args = tuple(func(arg.strip()) for arg, func in zip(args, validators))
            return args, True
        except FallbackError:
            return tuple(), True
        except InvalidArgError:
            return tuple(), False
        except ValueError:
            return args, False

    @staticmethod
    def validate_args(name: str, args: Sequence[Any]) -> tuple[tuple, bool]:
        """
        Validate the arguments of a tag.
        :param name: The name of the tag.
        :param args: The arguments of the tag.
        :return: A tuple containing the validated arguments and a boolean indicating if the tag is valid.
        """
        if is_special_tag(name):
            return tuple(args), True
        valid = False
        args = tuple(map(str, args))
        if is_simple_tag(name) and len(args) > 1:
            args = (args[0])
        if name == "t":
            if args:
                last = split_tags(args[-1], True)
                args, valid = Tag._validate_args(name, args[:-1])
                args = list(args)
                args.append(last)
        elif name in tag_args:
            args, valid = Tag._validate_args(name, args)
        return tuple(args), valid


def join_tags(tags: list[Tag], skip_comment: bool = False) -> str:
    """
    Join tags into text.
    :param tags: The tags to join.
    :param skip_comment: Whether to skip comments.
    :return: The joined text.
    """
    if any(not isinstance(tag, Tag) for tag in tags):
        raise TypeError("All elements must be of type Tag")
    text = ""
    in_tag = False
    for tag in filter(lambda x: not skip_comment or x.name != "Comment", tags):
        if tag.name in ("Drawing", "Text"):
            if in_tag:
                text += "}"
            text += str(tag.args[0])
            in_tag = False
        else:
            if not in_tag:
                text += "{"
            text += tag.to_string()
            in_tag = True
    if in_tag:
        text += "}"
    return text


def _parse_fs_arg(s: str) -> float | str:
    if not s:
        return 0
    if s.startswith(("+", "-")):
        return s
    else:
        return float(s)


def _parse_fn_arg(s: str) -> str:
    if s == "0":
        raise FallbackError
    return s


def _parse_an_arg(s: str) -> int:
    try:
        val = int(s)
        if 1 <= val <= 9:
            return val
        raise InvalidArgError
    except ValueError:
        raise InvalidArgError


def _parse_a_arg(s: str) -> int:
    try:
        val = int(s)
        if 1 <= val <= 11:
            return val if (val & 3) != 0 else 5
        raise InvalidArgError
    except ValueError:
        raise InvalidArgError


def _parse_be_arg(s: str) -> int:
    return max(0, int(parse_float(s) + 0.5))


def _parse_b_arg(s: str) -> int:
    val = parse_int32(s)
    if val == 0 or val == 1 or val >= 100:
        return val
    raise FallbackError


def _parse_boolean_arg(s: str) -> int:
    val = parse_int32(s)
    if val == 0 or val == 1:
        return val
    raise FallbackError


def _parse_kx_arg(s: str) -> float:
    val = parse_float(s)
    return int(val * 10) / 10


# def _parse_k_arg(s: str) -> float:
#     val = parse_float(s)
#     if val == 100:
#         raise FallbackError
#     return int(val * 10) / 10


def _parse_q_arg(s: str) -> int:
    val = parse_int32(s)
    if 0 <= val <= 3:
        return val
    raise InvalidArgError


tag_args = {
    "xbord": ((_positive_float,), ()),
    "ybord": ((_positive_float,), ()),
    "xshad": ((_float,), ()),
    "yshad": ((_float,), ()),
    "fax": ((_float,), ()),
    "fay": ((_float,), ()),
    "iclip": ((_int, _int, _int, _int), (AssDrawing,)),
    "blur": ((_positive_float,), ()),
    "fscx": ((_positive_float,), ()),
    "fscy": ((_positive_float,), ()),
    "fsc": ((),),
    "fsp": ((_float,),),
    "fs": ((_parse_fs_arg,), ()),
    "bord": ((_float,), ()),
    "move": ((_float, _float, _float, _float), (_float, _float, _float, _float, _int, _int)),
    "frx": ((_float,), ()),
    "fry": ((_float,), ()),
    "frz": ((_float,), ()),
    "fr": ((_float,), ()),
    "fn": ((_parse_fn_arg,), ()),
    "alpha": ((AssAlpha,), ()),
    "an": ((_int,),),
    "a": ((_int,),),
    "pos": ((_float, _float),),
    "fade": ((_int, _int), (AssAlpha, AssAlpha, AssAlpha, _int, _int, _int, _int)),
    "fad": ((_int, _int), (AssAlpha, AssAlpha, AssAlpha, _int, _int, _int, _int)),
    "org": ((_float, _float),),
    "clip": ((_int, _int, _int, _int), (AssDrawing,)),
    "c": ((_ass_color,), ()),
    "1c": ((_ass_color,), ()),
    "2c": ((_ass_color,), ()),
    "3c": ((_ass_color,), ()),
    "4c": ((_ass_color,), ()),
    "1a": ((AssAlpha,), ()),
    "2a": ((AssAlpha,), ()),
    "3a": ((AssAlpha,), ()),
    "4a": ((AssAlpha,), ()),
    "r": ((str,), ()),
    "be": ((_parse_be_arg,), ()),
    "b": ((_parse_b_arg,), ()),
    "i": ((_parse_boolean_arg,), ()),
    "kt": ((_parse_kx_arg,),),
    "kf": ((_parse_kx_arg,),),
    "K": ((_parse_kx_arg,),),
    "ko": ((_parse_kx_arg,),),
    "k": ((_parse_kx_arg,),),
    "shad": ((_positive_float,), ()),
    "s": ((_parse_boolean_arg,), ()),
    "u": ((_parse_boolean_arg,), ()),
    "pbo": ((_float,),),
    "p": ((_positive_int,), ()),
    "q": ((_parse_q_arg,), ()),
    "fe": ((_int,), ()),

    "t": ((_float,), (_int, _int), (_int, _int, _float)),
}


def split_tags(block: str, nested: bool = False) -> list[Tag]:
    """
    Split tags from an override tag block.
    :param block: The override tag block.
    :param nested: Whether the block is in a \t tag.
    :return: A list of Tag objects.
    """

    def split_args(args_str: str) -> list[str]:
        backslash_pos = args_str.find("\\")

        if backslash_pos == -1:
            return list(filter(lambda x: x.strip(), args_str.split(",")))

        first_part = args_str[:backslash_pos]
        result = list(filter(lambda x: x.strip(), first_part.split(",")))
        result.append(args_str[backslash_pos:])

        return result

    if not block:
        return []

    result = []
    tag_pattern = re.compile(r"\\([^(\\]+)(?:\(([^)]*)\)?)?")

    pos = 0

    while pos < len(block):
        next_tag = block.find("\\", pos)

        if next_tag > pos:
            comment = block[pos:next_tag]
            result.append(Tag("Comment", [comment]))
            pos = next_tag

        if next_tag == -1:
            if pos < len(block):
                result.append(Tag("Comment", [block[pos:]]))
            break

        match = tag_pattern.match(block, pos)
        if not match:
            pos += 1
            continue

        name = match.group(1)
        args_str = match.group(2)
        args = []

        if args_str:
            args = split_args(args_str)

        for tag in tag_args:
            if name.startswith(tag):
                if name != tag and is_simple_tag(tag):
                    args.append(name[len(tag):])
                name = tag
                break

        if name not in tag_args and not args:
            match_simple = re.match(r"([0-9]*[a-z]+)(.*)", name)
            if match_simple:
                tag_name, remaining = match_simple.groups()
                if remaining:
                    args.append(remaining)
                name = tag_name

        tag = Tag(name, args)
        if nested and not is_nestable_tag(name):
            tag.valid = False
        result.append(tag)

        pos = match.end()

    return result


def parse_tags(text: str) -> list[Tag]:
    """
    Parse tags from text.
    :param text: The text to parse.
    :return: A list of Tag objects.
    """
    result = []
    splits = OVERRIDE_BLOCK_PATTERN.split(text)
    drawing_mode = False
    for i, block in enumerate(splits):
        if i % 2 == 1:
            tags = split_tags(block)
            result.extend(tags)
            for tag in tags:
                if tag.name == "p" and tag.valid:
                    drawing_mode = tag.args and tag.args[0] > 0
        elif block:
            if drawing_mode:
                result.append(Tag("Drawing", [AssDrawing(block)]))
            else:
                result.append(Tag("Text", [block]))
    return result
