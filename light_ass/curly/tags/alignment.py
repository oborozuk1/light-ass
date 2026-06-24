from __future__ import annotations

from dataclasses import dataclass

from ...utils import TypeParser
from .base import SimpleTag


@dataclass
class AlignmentTag(SimpleTag[int]):
    tag_name = "an"
    _parse_param = staticmethod(TypeParser.parse_int)
    value: int | None


@dataclass
class LegacyAlignmentTag(SimpleTag[int]):
    tag_name = "a"
    _parse_param = staticmethod(TypeParser.parse_int)
    value: int | None
