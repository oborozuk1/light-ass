from light_ass.curly import OverrideBlock, TagParser
from light_ass.curly.tags import (
    BoldSimpleTag,
    FontSizeAbsoluteTag,
    PositionTag,
    Tag,
    TransformTag,
)
from light_ass.curly.tags.base import RawTag


class TestOverrideBlockInit:
    def test_default_empty(self):
        block = OverrideBlock()
        assert len(block) == 0
        assert list(block) == []

    def test_with_tags(self):
        bold = BoldSimpleTag(True)
        pos = PositionTag(10, 20)
        block = OverrideBlock([bold, pos])
        assert len(block) == 2
        assert block[0] is bold
        assert block[1] is pos


class TestOverrideBlockIteration:
    def test_iter(self):
        bold = BoldSimpleTag(True)
        pos = PositionTag(10, 20)
        block = OverrideBlock([bold, pos])
        result = list(block)
        assert result == [bold, pos]

    def test_reversed(self):
        bold = BoldSimpleTag(True)
        pos = PositionTag(10, 20)
        block = OverrideBlock([bold, pos])
        result = list(reversed(block))
        assert result == [pos, bold]

    def test_getitem_int(self):
        bold = BoldSimpleTag(True)
        pos = PositionTag(10, 20)
        block = OverrideBlock([bold, pos])
        assert block[0] is bold
        assert block[1] is pos

    def test_getitem_slice(self):
        bold = BoldSimpleTag(True)
        pos = PositionTag(10, 20)
        fs = FontSizeAbsoluteTag(48.0)
        block = OverrideBlock([bold, pos, fs])
        result = block[0:2]
        assert result == [bold, pos]

    def test_len_empty(self):
        assert len(OverrideBlock()) == 0

    def test_len_non_empty(self):
        assert len(OverrideBlock([BoldSimpleTag(True)])) == 1


class TestOverrideBlockGetTags:
    def test_all_tags(self):
        bold = BoldSimpleTag(True)
        pos = PositionTag(10, 20)
        block = OverrideBlock([bold, pos])
        tags = block.get_tags()
        assert tags == [bold, pos]

    def test_filter_by_class(self):
        bold = BoldSimpleTag(True)
        pos = PositionTag(10, 20)
        block = OverrideBlock([bold, pos])
        tags = block.get_tags(PositionTag)
        assert tags == [pos]

    def test_filter_by_tuple(self):
        bold = BoldSimpleTag(True)
        pos = PositionTag(10, 20)
        fs = FontSizeAbsoluteTag(48.0)
        block = OverrideBlock([bold, pos, fs])
        tags = block.get_tags((PositionTag, FontSizeAbsoluteTag))
        assert tags == [pos, fs]

    def test_include_transformed_tags(self):
        parser = TagParser()
        transform = TransformTag.from_raw(
            RawTag("t", (r"\fs48",), r"\t(\fs48)", TransformTag),
            parser=parser,
        )
        bold = BoldSimpleTag(True)
        block = OverrideBlock([bold, transform])
        tags = block.get_tags()
        assert bold in tags
        assert transform in tags
        fs_tags = [t for t in tags if isinstance(t, FontSizeAbsoluteTag)]
        assert len(fs_tags) == 1
        assert fs_tags[0].value == 48.0

    def test_exclude_transformed_tags(self):
        parser = TagParser()
        transform = TransformTag.from_raw(
            RawTag("t", (r"\fs48",), r"\t(\fs48)", TransformTag),
            parser=parser,
        )
        bold = BoldSimpleTag(True)
        block = OverrideBlock([bold, transform])
        tags = block.get_tags(include_transformed_tags=False)
        assert tags == [bold, transform]

    def test_no_matching_tags(self):
        bold = BoldSimpleTag(True)
        block = OverrideBlock([bold])
        tags = block.get_tags(PositionTag)
        assert tags == []


class TestOverrideBlockToAss:
    def test_with_braces(self):
        bold = BoldSimpleTag(True)
        block = OverrideBlock([bold])
        assert block.to_ass() == r"{\b1}"

    def test_without_braces(self):
        bold = BoldSimpleTag(True)
        block = OverrideBlock([bold])
        assert block.to_ass(include_brace=False) == r"\b1"

    def test_multiple_tags(self):
        bold = BoldSimpleTag(True)
        pos = PositionTag(10, 20)
        block = OverrideBlock([bold, pos])
        result = block.to_ass()
        assert result == r"{\b1\pos(10,20)}"

    def test_empty_block(self):
        block = OverrideBlock()
        assert block.to_ass() == "{}"

    def test_empty_block_no_brace(self):
        block = OverrideBlock()
        assert block.to_ass(include_brace=False) == ""
