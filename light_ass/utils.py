import re
from collections.abc import Callable
from itertools import takewhile

INT32_MIN = -2_147_483_648
INT32_MAX = 2_147_483_647


def clamp(val: int, min_: int, max_: int) -> int:
    return min(max(val, min_), max_)


def to_snake_case(text: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", text).lower()


def detect_file_encoding(file_path: str, sample_size: int = 1024) -> str | None:
    import codecs

    bom_map = {
        codecs.BOM_UTF8: "utf-8-sig",
        codecs.BOM_UTF16_LE: "utf-16-le",
        codecs.BOM_UTF16_BE: "utf-16-be",
        codecs.BOM_UTF32_LE: "utf-32-le",
        codecs.BOM_UTF32_BE: "utf-32-be",
    }

    with open(file_path, "rb") as f:
        sample = f.read(sample_size)

    for bom, encoding in bom_map.items():
        if sample.startswith(bom):
            return encoding

    test_encodings = ["utf-8", "gb18030", "big5", "shift_jis", "euc-kr", "iso-8859-1", "cp1252"]

    for encoding in test_encodings:
        try:
            sample.decode(encoding, errors="strict")
            return encoding
        except UnicodeDecodeError:
            continue

    return None


def validate_value(validator: Callable | tuple | dict, value: str):
    match validator:
        case validator if callable(validator):
            return validator(value)
        case tuple():
            typ_ = type(validator[0])
            if typ_(value) in validator:
                return typ_(value)
        case dict():
            if value in validator:
                return validator[value]
            if value in validator.values():
                return value
        case _:
            pass
    raise ValueError(f"Invalid value")


def parse_int32(s: str) -> int:
    s = s.lstrip(" \t")
    if not s:
        return 0

    sgn = 1
    if s[0] in "+-":
        sgn = 1 if s[0] == "+" else -1
        s = s[1:]

    num_str = "".join(takewhile(lambda x: x.isdigit(), s))
    num = sgn * int(num_str) if num_str else 0
    return clamp(num, INT32_MIN, INT32_MAX)


def parse_positive_int32(s: str) -> int:
    num = parse_int32(s)
    return num if num > 0 else 0


def parse_float(s: str) -> float:
    s = s.lstrip(" \t")
    if not s:
        return 0.0

    sgn = 1
    if s[0] in "+-":
        sgn = 1 if s[0] == "+" else -1
        s = s[1:]

    num_str = ".".join(
        map(
            lambda x: "".join(takewhile(lambda ch: ch.isdigit(), x)),
            s.split(".", 1)
        )
    )

    if num_str.startswith("."):
        num_str = "0" + num_str

    return sgn * float(num_str) if num_str and num_str else 0.0


def parse_positive_float(s: str) -> float:
    num = parse_float(s)
    return num if num > 0 else 0.0


def parse_ass_color(s: str):
    from .ass_types import AssColor

    s = s.lstrip("&H").lstrip(" \t")
    if s.startswith("+"):
        s = s[1:]
    if not tuple(takewhile(lambda x: x in "0123456789ABCDEF", s)):
        return AssColor(0, 0, 0)
    color = AssColor(s)
    rev_value = (color.a << 24) | (color.b << 16) | (color.g << 8) | color.r
    if rev_value >= INT32_MAX:
        color = AssColor(255, 255, 255)
    color.a = 0
    return color


def parse_ass_alpha(s: str):
    from .ass_types import AssAlpha

    s = s.lstrip("&H").lstrip(" \t")
    if s.startswith("+"):
        s = s[1:]
    num_str = "".join(takewhile(lambda x: x in "0123456789ABCDEF", s))
    if not num_str:
        return AssAlpha(0)
    val = int(num_str, 16) & 0xFF
    return AssAlpha(val)
