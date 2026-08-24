from __future__ import annotations

import copy
from unittest.mock import patch

import pytest

from light_ass.curly import TagParser
from light_ass.curly.tags import (
    AlignmentTag,
    BoldSimpleTag,
    FontNameTag,
    FontSizeAbsoluteTag,
    FontSizeRelativeTag,
    ItalicTag,
    LegacyAlignmentTag,
    PositionTag,
    RawTag,
    TransformTag,
)
from light_ass.curly.tags.base import _UNSET
from light_ass.types.align import Align
from light_ass.utils import TypeParser


def test_simple_tag_value_not_parsed_until_access():
    parser = TagParser()
    with patch.object(ItalicTag, "_parse_param", side_effect=TypeParser.parse_bool) as mock:
        block = parser.parse_block(r"\i1")
        tag = block.nodes[0]
        assert isinstance(tag, ItalicTag)
        assert tag._value is _UNSET
        assert mock.call_count == 0

        assert tag.value is True
        assert mock.call_count == 1

        assert tag.value is True
        assert mock.call_count == 1


def test_simple_tag_parse_failure_returns_none():
    parser = TagParser()
    block = parser.parse_block(r"\iabc")
    tag = block.nodes[0]
    assert isinstance(tag, ItalicTag)
    assert tag.value is None
    assert block.to_ass() == r"{\iabc}"


def test_simple_tag_empty_params_value_none():
    parser = TagParser()
    block = parser.parse_block(r"\i")
    tag = block.nodes[0]
    assert isinstance(tag, ItalicTag)
    assert tag.value is None
    assert block.to_ass() == r"{\i}"


def test_simple_tag_dirty_reserialize():
    parser = TagParser()
    block = parser.parse_block(r"\fs30")
    tag = block.nodes[0]
    assert isinstance(tag, FontSizeAbsoluteTag)
    assert block.to_ass() == r"{\fs30}"
    tag.value = 40
    assert block.to_ass() == r"{\fs40}"


def test_strict_mode_parses_eagerly():
    parser = TagParser(strict=True)
    with patch.object(ItalicTag, "_parse_param", side_effect=TypeParser.parse_bool) as mock:
        block = parser.parse_block(r"\i1")
        tag = block.nodes[0]
        assert isinstance(tag, ItalicTag)
        assert tag._value is not _UNSET
        assert mock.call_count == 1
        assert tag.value is True


def test_strict_mode_raises_on_multi_params():
    parser = TagParser(strict=True)
    with pytest.raises(ValueError, match="expected 1 param"):
        parser.parse_block(r"\fs(1,2)")


def test_parens_tag_failure_still_falls_back_to_raw():
    parser = TagParser()
    block = parser.parse_block(r"\pos(ab,cd)")
    node = block.nodes[0]
    assert isinstance(node, RawTag)
    assert not isinstance(node, PositionTag)
    assert block.to_ass() == r"{\pos(ab,cd)}"


def test_transform_modifier_lazy_and_cached():
    parser = TagParser()
    original = parser.parse_modifier
    calls: list[str] = []

    def spy(modifier: str, strict: bool | None = None):
        calls.append(modifier)
        return original(modifier, strict)

    parser.parse_modifier = spy  # type: ignore[method-assign]

    block = parser.parse_block(r"\t(0,100,\fs50)")
    tag = block.nodes[0]
    assert isinstance(tag, TransformTag)
    assert tag._modifier is _UNSET
    assert calls == []
    assert block.to_ass() == r"{\t(0,100,\fs50)}"

    modifier = tag.modifier
    assert calls == [r"\fs50"]
    assert tag.modifier is modifier
    assert calls == [r"\fs50"]

    fs = modifier.nodes[0]
    assert isinstance(fs, FontSizeAbsoluteTag)
    assert fs.value == 50.0
    assert tag.t1 == 0 and tag.t2 == 100


def test_transform_strict_parses_eagerly():
    parser = TagParser(strict=True)
    block = parser.parse_block(r"\t(\fs50)")
    tag = block.nodes[0]
    assert isinstance(tag, TransformTag)
    assert tag._modifier is not _UNSET
    assert isinstance(tag.modifier.nodes[0], FontSizeAbsoluteTag)


def test_transform_deepcopy_deferred_stays_lazy():
    parser = TagParser()
    block = parser.parse_block(r"\t(0,100,\fs50)")
    tag = block.nodes[0]
    assert isinstance(tag, TransformTag)

    tag_copy = copy.deepcopy(tag)
    assert tag_copy is not tag
    assert tag._modifier is _UNSET
    assert tag_copy._modifier is _UNSET

    fs = tag_copy.modifier.nodes[0]
    assert isinstance(fs, FontSizeAbsoluteTag)
    assert fs.value == 50.0
    assert tag._modifier is _UNSET


def test_transform_deepcopy_materialized_is_independent():
    parser = TagParser()
    block = parser.parse_block(r"\t(0,100,\fs50)")
    tag = block.nodes[0]
    assert isinstance(tag, TransformTag)
    original_modifier = tag.modifier

    tag_copy = copy.deepcopy(tag)
    assert tag_copy.modifier is not original_modifier
    assert tag_copy.modifier.to_ass() == original_modifier.to_ass()

    tag_copy.modifier.nodes[0].value = 99
    assert original_modifier.nodes[0].value == 50.0


def test_simple_tag_deepcopy_deferred_stays_lazy():
    parser = TagParser()
    block = parser.parse_block(r"\i1")
    tag = block.nodes[0]
    assert isinstance(tag, ItalicTag)
    assert tag._value is _UNSET

    tag_copy = copy.deepcopy(tag)
    assert tag_copy._value is _UNSET
    assert tag_copy.value is True
    assert tag._value is _UNSET


def test_alignment_lazy_and_conversion():
    parser = TagParser()
    block = parser.parse_block(r"\an8")
    tag = block.nodes[0]
    assert isinstance(tag, AlignmentTag)
    assert tag._value is _UNSET
    assert tag.value == Align(8)
    assert AlignmentTag(8).value == Align(8)


def test_legacy_alignment_lazy_and_conversion():
    parser = TagParser()
    block = parser.parse_block(r"\a6")
    tag = block.nodes[0]
    assert isinstance(tag, LegacyAlignmentTag)
    assert tag._value is _UNSET
    assert tag.value == Align.from_legacy(6)
    assert LegacyAlignmentTag(6).value == Align.from_legacy(6)


def test_font_size_dispatch_and_lazy():
    parser = TagParser()

    block = parser.parse_block(r"\fs30")
    tag = block.nodes[0]
    assert isinstance(tag, FontSizeAbsoluteTag)
    assert tag._value is _UNSET
    assert tag.value == 30.0

    block = parser.parse_block(r"\fs+2.5")
    tag = block.nodes[0]
    assert isinstance(tag, FontSizeRelativeTag)
    assert tag.value == 2.5


def test_font_name_zero_maps_to_none():
    parser = TagParser()
    block = parser.parse_block(r"\fn0")
    tag = block.nodes[0]
    assert isinstance(tag, FontNameTag)
    assert tag.value is None

    block = parser.parse_block(r"\fnArial")
    tag = block.nodes[0]
    assert isinstance(tag, FontNameTag)
    assert tag.value == "Arial"


def test_bold_stays_eager():
    parser = TagParser()
    block = parser.parse_block(r"\b1")
    tag = block.nodes[0]
    assert isinstance(tag, BoldSimpleTag)
    assert tag._value is not _UNSET
    assert tag.value is True


def test_get_tags_does_not_parse_unrelated_values():
    parser = TagParser()
    with patch.object(ItalicTag, "_parse_param", side_effect=TypeParser.parse_bool) as mock:
        block = parser.parse_block(r"\i1\pos(1,2)")
        tags = block.get_tags(ItalicTag)
        assert len(tags) == 1
        assert mock.call_count == 0
        assert tags[0].value is True
        assert mock.call_count == 1


def test_fx_line_round_trip_untouched():
    parser = TagParser()
    line = r"{\pos(100,200)\blur2\fs30\c&HFFFFFF&}{\k20}字{\t(0,100,\fs50\1c&H0000FF&)}幕"
    parsed = parser.parse(line, parse_escape_nodes=False)
    assert parsed.get_text() == line
