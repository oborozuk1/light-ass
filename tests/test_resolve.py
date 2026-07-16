import pytest

from light_ass import Document
from light_ass.curly import OverrideBlock, ParsedLine, TagParser
from light_ass.curly.tags import (
    BoldSimpleTag,
    FontSizeAbsoluteTag,
    OutlineAlphaTag,
    PrimaryAlphaTag,
    SecondaryAlphaTag,
    ShadowAlphaTag,
    TransformTag,
)
from light_ass.styles import Style, Styles


@pytest.fixture
def style():
    return Style(name="Default", fontsize=48.0, bold=True)


@pytest.fixture
def doc():
    st = Style(name="Default", fontsize=48.0, bold=True)
    doc = Document(styles=Styles([st]))
    doc.info["WrapStyle"] = 2
    return doc


@pytest.fixture
def parser():
    return TagParser()


class TestResolveBasic:
    def test_plain_text_passthrough(self, style, doc, parser):
        pl = parser.parse("Hello World")
        resolved = pl.resolve(style, doc)
        assert resolved.to_ass() == "Hello World"

    def test_bold_set_from_style(self, style, doc, parser):
        pl = parser.parse(r"{\b}Bold")
        resolved = pl.resolve(style, doc)
        assert resolved.to_ass() == r"{\b1}Bold"

    def test_fontsize_set_from_style(self, style, doc, parser):
        pl = parser.parse(r"{\fs}text")
        resolved = pl.resolve(style, doc)
        assert resolved.to_ass() == r"{\fs48}text"

    def test_bold_with_value_kept(self, style, doc, parser):
        pl = parser.parse(r"{\b1}Bold{\b0}normal")
        resolved = pl.resolve(style, doc)
        assert resolved.to_ass() == r"{\b1}Bold{\b0}normal"

    def test_multiple_blocks_preserved(self, style, doc, parser):
        pl = parser.parse(r"{\b}A{\b0}B")
        resolved = pl.resolve(style, doc)
        parts = [p for p in resolved.parts if isinstance(p, OverrideBlock)]
        assert len(parts) == 2


class TestResolveStructure:
    def test_returns_parsed_line(self, style, doc, parser):
        pl = parser.parse(r"{\b1}text")
        resolved = pl.resolve(style, doc)
        assert isinstance(resolved, ParsedLine)

    def test_override_block_structure_preserved(self, style, doc, parser):
        pl = parser.parse(r"{\b}text")
        resolved = pl.resolve(style, doc)
        override_blocks = [p for p in resolved.parts if isinstance(p, OverrideBlock)]
        assert len(override_blocks) == 1
        tags = list(override_blocks[0])
        assert len(tags) == 1
        assert isinstance(tags[0], BoldSimpleTag)
        assert tags[0].value is True

    def test_text_node_preserved(self, style, doc, parser):
        pl = parser.parse(r"{\b}Bold")
        resolved = pl.resolve(style, doc)
        from light_ass.curly.parsed_line import TextNode

        text_nodes = [p for p in resolved.parts if isinstance(p, TextNode)]
        assert len(text_nodes) == 1
        assert text_nodes[0].text == "Bold"

    def test_value_tags_not_lost(self, style, doc, parser):
        pl = parser.parse(r"{\b1\fs100}text")
        resolved = pl.resolve(style, doc)
        tags = resolved.get_tags()
        bold_tags = [t for t in tags if isinstance(t, BoldSimpleTag)]
        fs_tags = [t for t in tags if isinstance(t, FontSizeAbsoluteTag)]
        assert len(bold_tags) == 1
        assert bold_tags[0].value is True
        assert len(fs_tags) == 1
        assert fs_tags[0].value == 100.0

    def test_empty_block_preserved(self, style, doc, parser):
        pl = parser.parse(r"{}text")
        resolved = pl.resolve(style, doc)
        assert resolved.to_ass() == r"{}text"


class TestResolveAlphaExpansion:
    def test_alpha_expands_to_four(self, style, doc, parser):
        pl = parser.parse(r"{\alpha&H80&}")
        resolved = pl.resolve(style, doc)
        tags = resolved.get_tags()
        alpha_tags = [
            t
            for t in tags
            if isinstance(
                t,
                (
                    PrimaryAlphaTag,
                    SecondaryAlphaTag,
                    OutlineAlphaTag,
                    ShadowAlphaTag,
                ),
            )
        ]
        assert len(alpha_tags) == 4


class TestResolveTransformTag:
    def test_transform_tag_preserved(self, style, doc, parser):
        pl = parser.parse(r"{\b1\t(\fs48)}text")
        resolved = pl.resolve(style, doc)
        transform_tags = resolved.get_tags(TransformTag)
        assert len(transform_tags) == 1

    def test_transform_tag_to_ass_round_trip(self, style, doc, parser):
        original = r"{\b1\t(\fs48)}text"
        pl = parser.parse(original)
        resolved = pl.resolve(style, doc)
        assert resolved.to_ass() == original

    def test_transform_tag_modifier_resolved(self, style, doc, parser):
        pl = parser.parse(r"{\t(\fs)}text")
        resolved = pl.resolve(style, doc)
        transform_tags = resolved.get_tags(TransformTag)
        assert len(transform_tags) == 1
        modifier_tags = list(transform_tags[0].modifier)
        fs_tags = [t for t in modifier_tags if isinstance(t, FontSizeAbsoluteTag)]
        assert len(fs_tags) == 1
        assert fs_tags[0].value == 48.0


class TestResolveRoundTrip:
    def test_complex_round_trip(self, style, doc, parser):
        original = r"{\b1\fs100}Bold{\b0\fs48}normal"
        pl = parser.parse(original)
        resolved = pl.resolve(style, doc)
        assert resolved.to_ass() == original

    def test_resolve_then_get_tags(self, style, doc, parser):
        pl = parser.parse(r"{\b1\fs100}text")
        resolved = pl.resolve(style, doc)
        tags = resolved.get_tags()
        assert len(tags) >= 2

    def test_resolve_empty_line(self, style, doc, parser):
        pl = parser.parse("")
        resolved = pl.resolve(style, doc)
        assert resolved.to_ass() == ""
