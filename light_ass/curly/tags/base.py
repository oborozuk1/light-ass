from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, ClassVar, Generic, Self, TypeVar

from ...utils import Formatter

if TYPE_CHECKING:
    from ..parser import TagParser

VT = TypeVar("VT")


class EffectPolicy:
    @staticmethod
    def simplify_in_block(tags: list[tuple[Tag, int]]) -> set[int]:
        return {idx for _, idx in tags}

    @staticmethod
    def simplify_across_blocks(blocks: list[list[tuple[Tag, int]]]) -> set[tuple[int, int]]:
        return {(p, idx) for p, block in enumerate(blocks) for _, idx in block}


class FirstPolicy(EffectPolicy):
    @staticmethod
    def simplify_in_block(tags: list[tuple[Tag, int]]) -> set[int]:
        for _, idx in tags:
            return {idx}
        return set()

    @staticmethod
    def simplify_across_blocks(blocks: list[list[tuple[Tag, int]]]) -> set[tuple[int, int]]:
        for p, block in enumerate(blocks):
            for _, idx in block:
                return {(p, idx)}
        return set()


class LastPolicy(EffectPolicy):
    @staticmethod
    def simplify_in_block(tags: list[tuple[Tag, int]]) -> set[int]:
        for _, idx in reversed(tags):
            return {idx}
        return set()

    @staticmethod
    def simplify_across_blocks(blocks: list[list[tuple[Tag, int]]]) -> set[tuple[int, int]]:
        for p in range(len(blocks) - 1, -1, -1):
            for _, idx in reversed(blocks[p]):
                return {(p, idx)}
        return set()


class OverridePolicy(EffectPolicy):
    @staticmethod
    def simplify_in_block(tags: list[tuple[Tag, int]]) -> set[int]:
        for _, idx in reversed(tags):
            return {idx}
        return set()


class AccumulatePolicy(EffectPolicy):
    pass


@dataclass(slots=True, frozen=True, unsafe_hash=True)
class EffectGroup:
    name: str
    policy: type[EffectPolicy] = OverridePolicy


@dataclass(slots=True)
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
    effect_group: ClassVar[EffectGroup]
    _raw: RawTag | None = field(kw_only=True, default=None, repr=False, compare=False)
    _dirty: bool = field(init=False, default=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        self._dirty = False

    def __setattr__(self, name: str, value: VT) -> None:
        object.__setattr__(self, "_dirty", True)
        object.__setattr__(self, name, value)

    def normalize(self) -> None:
        pass

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

    def __init_subclass__(cls, **kwargs: Any) -> None:
        if "effect_group" not in cls.__dict__ and not any(
            "effect_group" in base.__dict__ for base in cls.mro()[1:]
        ):
            cls.effect_group = EffectGroup(cls.tag_name, OverridePolicy)

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
    def __init_subclass__(cls, **kwargs: Any) -> None:
        if "effect_group" not in cls.__dict__ and not any(
            "effect_group" in base.__dict__ for base in cls.mro()[1:]
        ):
            cls.effect_group = EffectGroup(cls.tag_name, FirstPolicy)

    def _serialize(self) -> str:
        params = ",".join(Formatter.format(param) for param in self.get_params())
        return f"\\{self.tag_name}({params})"
