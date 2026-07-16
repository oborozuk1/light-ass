from light_ass.curly.tags.alignment import AlignmentTag, LegacyAlignmentTag
from light_ass.curly.tags.base import RawTag
from light_ass.curly.tags.color import (
    AlphaTag,
    OutlineAlphaTag,
    OutlineColorTag,
    PrimaryAlphaTag,
    PrimaryColorTag,
    SecondaryAlphaTag,
    SecondaryColorTag,
    ShadowAlphaTag,
    ShadowColorTag,
)
from light_ass.curly.tags.font import (
    FontEncodingTag,
    FontNameTag,
    FontSizeRelativeTag,
    FontSizeTag,
    LetterSpacingTag,
)
from light_ass.curly.tags.geometry import (
    DrawingBaselineOffsetTag,
    DrawingModeTag,
    RotateXTag,
    RotateYTag,
    RotateZTag,
    ScaleTag,
    ScaleXTag,
    ScaleYTag,
    ShearXTag,
    ShearYTag,
)
from light_ass.curly.tags.karaoke import (
    KaraokeOutlineTag,
    KaraokeSweepTag,
    KaraokeTag,
    KaraokeTimeTag,
)
from light_ass.curly.tags.style import (
    BlurEdgeTag,
    BlurTag,
    BoldSimpleTag,
    BoldWeightTag,
    BorderTag,
    BorderXTag,
    BorderYTag,
    ItalicTag,
    ResetStyleTag,
    ShadowTag,
    ShadowXTag,
    ShadowYTag,
    StrikeoutTag,
    UnderlineTag,
    WrapStyleTag,
)
from light_ass.types import AssAlpha, AssColor


def _parse_simple(cls, value_str):
    return cls.from_raw(RawTag(cls.tag_name, (value_str,), f"\\{cls.tag_name}{value_str}", cls))


def _parse_simple_no_value(cls):
    return cls.from_raw(RawTag(cls.tag_name, (), f"\\{cls.tag_name}", cls))


class TestAlignmentTags:
    def test_alignment_tag(self):
        t = _parse_simple(AlignmentTag, "5")
        assert t.value == 5

    def test_alignment_tag_no_value(self):
        t = _parse_simple_no_value(AlignmentTag)
        assert t.value is None

    def test_alignment_tag_serialize(self):
        t = _parse_simple(AlignmentTag, "5")
        assert t.to_ass() == "\\an5"

    def test_alignment_tag_none_serialize(self):
        t = _parse_simple_no_value(AlignmentTag)
        assert t.to_ass() == "\\an"

    def test_legacy_alignment(self):
        t = _parse_simple(LegacyAlignmentTag, "3")
        assert t.value == 3


class TestAlphaTags:
    def test_alpha_tag(self):
        t = _parse_simple(AlphaTag, "&H80&")
        assert t.value == AssAlpha(0x80)

    def test_primary_alpha(self):
        t = _parse_simple(PrimaryAlphaTag, "&HFF&")
        assert t.value == AssAlpha(0xFF)

    def test_secondary_alpha(self):
        t = _parse_simple(SecondaryAlphaTag, "&H40&")
        assert t.value == AssAlpha(0x40)

    def test_outline_alpha(self):
        t = _parse_simple(OutlineAlphaTag, "&H00&")
        assert t.value == AssAlpha(0)

    def test_shadow_alpha(self):
        t = _parse_simple(ShadowAlphaTag, "&H80&")
        assert t.value == AssAlpha(0x80)

    def test_alpha_serialize(self):
        t = _parse_simple(AlphaTag, "&H80&")
        assert t.to_ass() == "\\alpha&H80&"


class TestColorTags:
    def test_primary_color(self):
        t = _parse_simple(PrimaryColorTag, "&H00FF00&")
        assert t.value == AssColor(0, 255, 0)

    def test_primary_color_serialize(self):
        t = _parse_simple(PrimaryColorTag, "&H00FF00&")
        assert "1c" in t.to_ass()
        assert "00FF00" in t.to_ass()

    def test_secondary_color(self):
        t = _parse_simple(SecondaryColorTag, "&H0000FF&")
        assert t.value == AssColor(255, 0, 0)

    def test_outline_color(self):
        t = _parse_simple(OutlineColorTag, "&HFF0000&")
        assert t.value == AssColor(0, 0, 255)

    def test_shadow_color(self):
        t = _parse_simple(ShadowColorTag, "&H000000&")
        assert t.value == AssColor(0, 0, 0)

    def test_primary_color_alias(self):
        from light_ass.curly.tags.base import RawTag

        t = PrimaryColorTag.from_raw(RawTag("c", ("&H00FF00&",), "\\c&H00FF00&", PrimaryColorTag))
        assert t.value == AssColor(0, 255, 0)
        assert "c" in t.to_ass()
        assert "00FF00" in t.to_ass()


class TestFontTags:
    def test_font_size_absolute(self):
        from light_ass.curly.tags.base import RawTag

        t = FontSizeTag.from_raw(RawTag("fs", ("48",), "\\fs48", FontSizeTag))
        assert t.value == 48.0

    def test_font_size_relative(self):
        from light_ass.curly.tags.base import RawTag

        t = FontSizeTag.from_raw(RawTag("fs", ("+10",), "\\fs+10", FontSizeTag))
        assert isinstance(t, FontSizeRelativeTag)
        assert t.value == 10.0

    def test_font_size_relative_negative(self):
        from light_ass.curly.tags.base import RawTag

        t = FontSizeTag.from_raw(RawTag("fs", ("-5",), "\\fs-5", FontSizeTag))
        assert isinstance(t, FontSizeRelativeTag)
        assert t.value == -5.0

    def test_font_size_absolute_serialize(self):
        from light_ass.curly.tags.base import RawTag

        t = FontSizeTag.from_raw(RawTag("fs", ("48",), "\\fs48", FontSizeTag))
        result = t.to_ass()
        assert "fs" in result

    def test_font_name(self):
        t = _parse_simple(FontNameTag, "Arial")
        assert t.value == "Arial"

    def test_font_name_serialize(self):
        t = _parse_simple(FontNameTag, "Arial")
        assert t.to_ass() == "\\fnArial"

    def test_font_encoding(self):
        t = _parse_simple(FontEncodingTag, "1")
        assert t.value == 1

    def test_letter_spacing(self):
        t = _parse_simple(LetterSpacingTag, "2.5")
        assert t.value == 2.5


class TestGeometryTags:
    def test_scale_x(self):
        t = _parse_simple(ScaleXTag, "150")
        assert t.value == 150.0

    def test_scale_y(self):
        t = _parse_simple(ScaleYTag, "200")
        assert t.value == 200.0

    def test_scale_tag_no_value(self):
        t = ScaleTag.from_raw(RawTag("fsc", (), "\\fsc", ScaleTag))
        assert t.to_ass() == "\\fsc"

    def test_rotate_z(self):
        t = _parse_simple(RotateZTag, "45")
        assert t.value == 45.0

    def test_rotate_z_alias(self):
        from light_ass.curly.tags.base import RawTag

        t = RotateZTag.from_raw(RawTag("fr", ("90",), "\\fr90", RotateZTag))
        assert t.value == 90.0

    def test_rotate_x(self):
        t = _parse_simple(RotateXTag, "30")
        assert t.value == 30.0

    def test_rotate_y(self):
        t = _parse_simple(RotateYTag, "60")
        assert t.value == 60.0

    def test_shear_x(self):
        t = _parse_simple(ShearXTag, "0.5")
        assert t.value == 0.5

    def test_shear_y(self):
        t = _parse_simple(ShearYTag, "0.3")
        assert t.value == 0.3

    def test_drawing_mode(self):
        t = _parse_simple(DrawingModeTag, "1")
        assert t.value == 1

    def test_drawing_baseline_offset(self):
        t = _parse_simple(DrawingBaselineOffsetTag, "5")
        assert t.value == 5.0


class TestKaraokeTags:
    def test_karaoke(self):
        t = _parse_simple(KaraokeTag, "50")
        assert t.value == 50.0

    def test_karaoke_sweep(self):
        t = _parse_simple(KaraokeSweepTag, "100")
        assert t.value == 100.0

    def test_karaoke_sweep_alias(self):
        from light_ass.curly.tags.base import RawTag

        t = KaraokeSweepTag.from_raw(RawTag("K", ("200",), "\\K200", KaraokeSweepTag))
        assert t.value == 200.0

    def test_karaoke_outline(self):
        t = _parse_simple(KaraokeOutlineTag, "80")
        assert t.value == 80.0

    def test_karaoke_time(self):
        t = _parse_simple(KaraokeTimeTag, "120")
        assert t.value == 120.0


class TestStyleTags:
    def test_bold_simple_true(self):
        t = _parse_simple(BoldSimpleTag, "1")
        assert t.value is True

    def test_bold_simple_false(self):
        t = _parse_simple(BoldSimpleTag, "0")
        assert t.value is False

    def test_bold_weight(self):
        from light_ass.curly.tags.base import RawTag

        t = BoldWeightTag(value=700, _raw=RawTag("b", ("700",), "\\b700", BoldWeightTag))
        assert t.value == 700

    def test_bold_dispatch(self):
        from light_ass.curly.tags.base import RawTag
        from light_ass.curly.tags.style import BoldTag

        t1 = BoldTag.from_raw(RawTag("b", ("1",), "\\b1", BoldTag))
        assert isinstance(t1, BoldSimpleTag)
        t2 = BoldTag.from_raw(RawTag("b", ("700",), "\\b700", BoldTag))
        assert isinstance(t2, BoldWeightTag)

    def test_italic(self):
        t = _parse_simple(ItalicTag, "1")
        assert t.value is True

    def test_italic_false(self):
        t = _parse_simple(ItalicTag, "0")
        assert t.value is False

    def test_underline(self):
        t = _parse_simple(UnderlineTag, "1")
        assert t.value is True

    def test_strikeout(self):
        t = _parse_simple(StrikeoutTag, "1")
        assert t.value is True

    def test_border(self):
        t = _parse_simple(BorderTag, "3")
        assert t.value == 3.0

    def test_border_x(self):
        t = _parse_simple(BorderXTag, "2.5")
        assert t.value == 2.5

    def test_border_y(self):
        t = _parse_simple(BorderYTag, "1.5")
        assert t.value == 1.5

    def test_shadow(self):
        t = _parse_simple(ShadowTag, "3")
        assert t.value == 3.0

    def test_shadow_x(self):
        t = _parse_simple(ShadowXTag, "2")
        assert t.value == 2.0

    def test_shadow_y(self):
        t = _parse_simple(ShadowYTag, "1")
        assert t.value == 1.0

    def test_blur_edge(self):
        t = _parse_simple(BlurEdgeTag, "2")
        assert t.value == 2.0

    def test_blur(self):
        t = _parse_simple(BlurTag, "0.6")
        assert t.value == 0.6

    def test_wrap_style(self):
        t = _parse_simple(WrapStyleTag, "2")
        assert t.value == 2

    def test_reset_style(self):
        t = _parse_simple(ResetStyleTag, "Default")
        assert t.value == "Default"

    def test_reset_style_no_value(self):
        t = _parse_simple_no_value(ResetStyleTag)
        assert t.value is None


class TestTagDirtyTracking:
    def test_dirty_on_modify(self):
        t = _parse_simple(AlignmentTag, "5")
        assert t._dirty is False
        t.value = 7
        assert t._dirty is True

    def test_to_ass_after_dirty(self):
        t = _parse_simple(AlignmentTag, "5")
        t.value = 7
        result = t.to_ass()
        assert "an7" in result
