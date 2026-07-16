from __future__ import annotations

from ...utils import TypeParser
from .base import RawTag, SimpleTag


class ScaleXTag(SimpleTag[float]):
    __slots__ = ()

    tag_name = "fscx"
    _parse_param = staticmethod(TypeParser.parse_float)

    def normalize(self) -> None:
        if self.value is not None:
            self.value = max(0.0, self.value)


class ScaleYTag(SimpleTag[float]):
    __slots__ = ()

    tag_name = "fscy"
    _parse_param = staticmethod(TypeParser.parse_float)

    def normalize(self) -> None:
        if self.value is not None:
            self.value = max(0.0, self.value)


class ScaleTag(SimpleTag[None]):
    __slots__ = ()

    tag_name = "fsc"

    def __init__(self, value: None = None, _raw: RawTag | None = None) -> None:
        super().__init__(None, _raw=_raw)

    @staticmethod
    def _parse_param(param: str) -> None:
        raise ValueError(f"{ScaleTag.__name__} does not accept parameters")

    def get_params(self) -> tuple[None]:
        return (None,)

    def _serialize(self) -> str:
        return "\\fsc"


class RotateXTag(SimpleTag[float]):
    __slots__ = ()

    tag_name = "frx"
    _parse_param = staticmethod(TypeParser.parse_float)


class RotateYTag(SimpleTag[float]):
    __slots__ = ()

    tag_name = "fry"
    _parse_param = staticmethod(TypeParser.parse_float)


class RotateZTag(SimpleTag[float]):
    __slots__ = ()

    tag_name = "frz"
    aliases = ("fr",)
    _parse_param = staticmethod(TypeParser.parse_float)


class ShearXTag(SimpleTag[float]):
    __slots__ = ()

    tag_name = "fax"
    _parse_param = staticmethod(TypeParser.parse_float)


class ShearYTag(SimpleTag[float]):
    __slots__ = ()

    tag_name = "fay"
    _parse_param = staticmethod(TypeParser.parse_float)


class DrawingModeTag(SimpleTag[int]):
    __slots__ = ()

    tag_name = "p"
    _parse_param = staticmethod(TypeParser.parse_int)

    def normalize(self) -> None:
        if self.value is not None:
            self.value = max(0, self.value)


class DrawingBaselineOffsetTag(SimpleTag[float]):
    __slots__ = ()

    tag_name = "pbo"
    _parse_param = staticmethod(TypeParser.parse_float)
