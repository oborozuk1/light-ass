from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar, Generic, Self, TypeVar

from ...utils import Formatter

if TYPE_CHECKING:
    from ..parser import TagParser


VT = TypeVar("VT")


@dataclass(slots=True, frozen=True)
class RawTag:
    name: str
    params: tuple[str, ...]
    raw_str: str
    cls: type[Tag] | None = field(default=None, repr=False, compare=False)

    def to_ass(self) -> str:
        return self.raw_str


@dataclass(slots=True)
class Tag(ABC):
    tag_name: ClassVar[str]
    aliases: ClassVar[tuple[str, ...]] = tuple()
    _raw: RawTag | None = field(kw_only=True, default=None, repr=False, compare=False)
    _dirty: bool = field(init=False, default=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        self._dirty = False

    def __setattr__(self, name: str, value: VT) -> None:
        object.__setattr__(self, "_dirty", True)
        object.__setattr__(self, name, value)

    @classmethod
    @abstractmethod
    def from_raw(cls, raw: RawTag, strict: bool = False, parser: TagParser | None = None) -> Tag:
        pass

    @abstractmethod
    def _serialize(self) -> str:
        pass

    @abstractmethod
    def get_params(self) -> tuple[object, ...]:
        pass

    def to_ass(self) -> str:
        if self._raw and not self._dirty:
            return self._raw.raw_str

        return self._serialize()


@dataclass(slots=True)
class SimpleTag(Tag, ABC, Generic[VT]):
    value: VT | None = None

    @staticmethod
    @abstractmethod
    def _parse_param(param: str) -> VT:
        pass

    @classmethod
    def from_raw(cls, raw: RawTag, strict: bool = False, parser: TagParser | None = None) -> Self:
        if len(raw.params) == 0:
            return cls(None, _raw=raw)

        if len(raw.params) > 1 and strict:
            raise ValueError(f"{cls.__name__} expected 1 param, got {len(raw.params)}")

        try:
            return cls(cls._parse_param(raw.params[0]), _raw=raw)
        except ValueError:
            return cls(None, _raw=raw)

    def get_params(self) -> tuple[VT | None]:
        return (self.value,)

    def _serialize(self) -> str:
        if self.value is None:
            return f"\\{self.tag_name}"
        return f"\\{self.tag_name}{Formatter.format(self.value)}"


@dataclass(slots=True)
class ParensTag(Tag, ABC):
    def _serialize(self) -> str:
        params = ",".join(Formatter.format(param) for param in self.get_params())
        return f"\\{self.tag_name}({params})"
