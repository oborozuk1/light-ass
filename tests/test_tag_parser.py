import pytest

from light_ass.curly.parser import (
    CommentNode,
    HardSpaceNode,
    NewlineNode,
    ParsedLine,
    SoftNewlineNode,
    TagParser,
    TextNode,
)
from light_ass.curly.tags import (
    BoldSimpleTag,
    BoldTag,
    PositionTag,
    PrimaryColorTag,
    RawTag,
)
from light_ass.types import AssColor


class TestParsedLine:
    def test_get_text(self):
        parts = [TextNode("Hello"), PositionTag(10, 20)]
        pl = ParsedLine(parts=parts)
        text = pl.get_text()
        assert "Hello" in text

    def test_get_plain_text(self):
        parts = [TextNode("Hello"), BoldSimpleTag(True)]
        pl = ParsedLine(parts=parts)
        assert pl.get_plain_text() == "Hello"

    def test_get_tags(self):
        tag = BoldSimpleTag(True)
        parts = [TextNode("Hello"), tag]
        pl = ParsedLine(parts=parts)
        tags = pl.get_tags()
        assert tags == [tag]

    def test_to_ass(self):
        parts = [TextNode("Hello")]
        pl = ParsedLine(parts=parts)
        result = pl.to_ass()
        assert "Hello" in result

    def test_len(self):
        parts = [TextNode("A"), BoldSimpleTag(True)]
        pl = ParsedLine(parts=parts)
        assert len(pl) == 2


class TestTagParserInit:
    def test_default_init(self):
        p = TagParser()
        assert p.strict is False
        assert p.escape_brace is True

    def test_strict_init(self):
        p = TagParser(strict=True)
        assert p.strict is True


class TestTagParserFreeze:
    def test_freeze(self):
        p = TagParser()
        p.freeze()
        with pytest.raises(AttributeError):
            p.strict = True

    def test_unfreeze(self):
        p = TagParser()
        p.freeze()
        p.unfreeze()
        p.strict = True
        assert p.strict is True


class TestTagParserSplitParams:
    def test_simple(self):
        result = TagParser.split_params("1,2,3")
        assert result == ["1", "2", "3"]

    def test_single(self):
        result = TagParser.split_params("42")
        assert result == ["42"]

    def test_with_comment(self):
        result = TagParser.split_params("1,2\\comment")
        assert result == ["1", "2", "\\comment"]

    def test_strip_whitespace(self):
        result = TagParser.split_params(" 1 , 2 ")
        assert result == ["1", "2"]


class TestTagParserFindTagCls:
    def test_exact_match(self):
        p = TagParser()
        result = p.find_tag_cls("pos")
        assert result is not None
        assert result[0] == "pos"

    def test_fuzzy_match(self):
        p = TagParser()
        result = p.find_tag_cls("posabc")
        assert result is not None
        assert result[0] == "pos"

    def test_alias_match(self):
        p = TagParser()
        result = p.find_tag_cls("c")
        assert result is not None
        assert result[0] == "c"

    def test_no_match(self):
        p = TagParser()
        result = p.find_tag_cls("zzz_nonexistent")
        assert result is None


class TestTagParserParseBlock:
    def test_simple_tag(self):
        p = TagParser()
        result = p.parse_block("\\b1")
        assert len(result) == 1
        assert isinstance(result[0], BoldTag)

    def test_multiple_tags(self):
        p = TagParser()
        result = p.parse_block("\\b1\\i1")
        assert len(result) == 2

    def test_pos_tag(self):
        p = TagParser()
        result = p.parse_block("\\pos(100,200)")
        assert len(result) == 1
        assert isinstance(result[0], PositionTag)
        assert result[0].x == 100
        assert result[0].y == 200

    def test_comment_node(self):
        p = TagParser()
        result = p.parse_block("hello")
        assert len(result) == 1
        assert isinstance(result[0], CommentNode)
        assert result[0].text == "hello"

    def test_unknown_tag_becomes_raw(self):
        p = TagParser()
        result = p.parse_block("\\xyzzz_unknown42")
        assert len(result) >= 1
        assert isinstance(result[-1], RawTag) or any(isinstance(r, RawTag) for r in result)

    def test_color_with_ampersand(self):
        p = TagParser()
        result = p.parse_block("\\c&HFF0000&")
        assert len(result) == 1
        tag = result[0]
        assert isinstance(tag, PrimaryColorTag)

    def test_strict_braces_not_allowed(self):
        p = TagParser(strict=True)
        with pytest.raises(ValueError):
            p.parse_block("\\b1{extra}")


class TestTagParserParse:
    def test_plain_text(self):
        p = TagParser()
        result = p.parse("Hello World")
        assert len(result.parts) == 1
        assert isinstance(result.parts[0], TextNode)
        assert result.parts[0].text == "Hello World"

    def test_text_with_tags(self):
        p = TagParser()
        result = p.parse("{\\b1}Bold{\\b0}")
        assert len(result.parts) >= 2

    def test_escape_brace(self):
        p = TagParser(escape_brace=True)
        result = p.parse("\\{Not a tag\\}")
        assert len(result.parts) > 0

    def test_no_starting_brace(self):
        p = TagParser()
        result = p.parse("Hello {\\b1}World")
        assert len(result.parts) >= 3

    def test_parse_escape_nodes(self):
        p = TagParser()
        result = p.parse("Line 1\\NLine 2", parse_escape_nodes=True)
        nodes = [p for p in result.parts if isinstance(p, NewlineNode)]
        assert len(nodes) == 1

    def test_parse_soft_newline(self):
        p = TagParser()
        result = p.parse("A\\nB", parse_escape_nodes=True)
        nodes = [p for p in result.parts if isinstance(p, SoftNewlineNode)]
        assert len(nodes) == 1

    def test_parse_hard_space(self):
        p = TagParser()
        result = p.parse("A\\hB", parse_escape_nodes=True)
        nodes = [p for p in result.parts if isinstance(p, HardSpaceNode)]
        assert len(nodes) == 1

    def test_multiple_escapes(self):
        p = TagParser()
        result = p.parse("A\\N\\NB", parse_escape_nodes=True)
        nodes = [p for p in result.parts if isinstance(p, NewlineNode)]
        assert len(nodes) == 1
        assert nodes[0].amount == 2


class TestTagParserColors:
    def test_primary_color(self):
        p = TagParser()
        result = p.parse("{\\1c&H00FF00&}Green")
        tags = result.get_tags()
        assert len(tags) == 1
        assert isinstance(tags[0], PrimaryColorTag)
        assert tags[0].value == AssColor(0, 255, 0)

    def test_secondary_color(self):
        p = TagParser()
        result = p.parse("{\\2c&H0000FF&}")
        tags = result.get_tags()
        assert len(tags) == 1
        assert tags[0].value == AssColor(255, 0, 0)

    def test_color_alias_c(self):
        p = TagParser()
        result = p.parse("{\\c&H0000FF&}")
        tags = result.get_tags()
        assert len(tags) == 1
        assert isinstance(tags[0], PrimaryColorTag)
