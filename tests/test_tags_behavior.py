from __future__ import annotations

import pytest

from light_ass.curly import OverrideBlock, TagParser
from light_ass.curly.tags import (
    BlurEdgeTag,
    BlurTag,
    BoldSimpleTag,
    BoldTag,
    BoldWeightTag,
    BorderTag,
    DrawingModeTag,
    FadeComplexTag,
    FontSizeAbsoluteTag,
    MoveTag,
    PositionTag,
    ResetStyleTag,
    ScaleTag,
    ScaleXTag,
    ShadowTag,
    WrapStyleTag,
)
from light_ass.curly.tags.base import (
    EffectGroup,
    FirstPolicy,
    OverridePolicy,
    RawTag,
)
from light_ass.types.align import Align


class TestTagEqualityHash:
    def test_eq_same_params(self):
        assert BorderTag(3.0) == BorderTag(3.0)

    def test_eq_diff_params(self):
        assert BorderTag(3.0) != BorderTag(5.0)

    def test_eq_cross_type(self):
        assert BorderTag(3.0) != ShadowTag(3.0)

    def test_eq_non_tag(self):
        assert BorderTag(3.0).__eq__(3.0) is NotImplemented

    def test_eq_parens_tag(self):
        assert PositionTag(1.0, 2.0) == PositionTag(1.0, 2.0)
        assert PositionTag(1.0, 2.0) != PositionTag(1.0, 3.0)


class TestTagRepr:
    def test_simple_repr(self):
        assert repr(BorderTag(3.0)) == "BorderTag(value=3.0)"

    def test_simple_none_repr(self):
        assert repr(BorderTag(None)) == "BorderTag(value=None)"

    def test_parens_repr(self):
        assert repr(PositionTag(1.0, 2.0)) == "PositionTag(x=1.0, y=2.0)"

    def test_move_repr(self):
        assert repr(MoveTag(0.0, 0.0, 100.0, 200.0)) == "MoveTag(x1=0.0, y1=0.0, x2=100.0, y2=200.0)"

    def test_fade_complex_repr(self):
        r = repr(FadeComplexTag(255, 128, 0, 0, 1000, 2000, 3000))
        assert r == "FadeComplexTag(a1=255, a2=128, a3=0, t1=0, t2=1000, t3=2000, t4=3000)"


class TestSlots:
    def test_simple_tag_rejects_new_attr(self):
        with pytest.raises(AttributeError):
            BorderTag(3.0).foo = 1

    def test_parens_tag_rejects_new_attr(self):
        with pytest.raises(AttributeError):
            PositionTag(1.0, 2.0).foo = 1

    def test_no_instance_dict(self):
        t = BorderTag(3.0)
        assert not hasattr(t, "__dict__")

    def test_parens_no_instance_dict(self):
        t = PositionTag(1.0, 2.0)
        assert not hasattr(t, "__dict__")


class TestDirtyTracking:
    def test_construct_not_dirty_simple(self):
        assert BorderTag(3.0)._dirty is False

    def test_construct_not_dirty_parens(self):
        assert PositionTag(1.0, 2.0)._dirty is False

    def test_construct_not_dirty_move(self):
        assert MoveTag(0.0, 0.0, 100.0, 200.0)._dirty is False

    def test_modify_marks_dirty_simple(self):
        t = BorderTag(3.0)
        t.value = 5.0
        assert t._dirty is True

    def test_modify_marks_dirty_parens(self):
        t = PositionTag(1.0, 2.0)
        t.x = 9.0
        assert t._dirty is True

    def test_modify_marks_dirty_move(self):
        t = MoveTag(0.0, 0.0, 100.0, 200.0)
        t.x2 = 50.0
        assert t._dirty is True

    def test_to_ass_uses_raw_when_clean(self):
        raw = RawTag("bord", ("3",), "\\bord3", BorderTag)
        t = BorderTag.from_raw(raw)
        assert t.to_ass() == "\\bord3"

    def test_to_ass_re_serializes_when_dirty(self):
        raw = RawTag("bord", ("3",), "\\bord3", BorderTag)
        t = BorderTag.from_raw(raw)
        t.value = 5.0
        assert t.to_ass() == "\\bord5"

    def test_to_ass_re_serializes_parens_when_dirty(self):
        raw = RawTag("pos", ("1", "2"), "\\pos(1,2)", PositionTag)
        t = PositionTag.from_raw(raw)
        assert t.to_ass() == "\\pos(1,2)"
        t.x = 9.0
        assert t.to_ass() == "\\pos(9,2)"


class TestNormalize:
    def test_border_clamps_negative(self):
        t = BorderTag(-2.0)
        t.normalize()
        assert t.value == 0.0

    def test_border_keeps_positive(self):
        t = BorderTag(3.0)
        t.normalize()
        assert t.value == 3.0

    def test_border_none_stays_none(self):
        t = BorderTag(None)
        t.normalize()
        assert t.value is None

    def test_shadow_clamps_negative(self):
        t = ShadowTag(-1.0)
        t.normalize()
        assert t.value == 0.0

    def test_blur_clamps_negative(self):
        t = BlurTag(-0.5)
        t.normalize()
        assert t.value == 0.0

    def test_blur_edge_clamps_negative(self):
        t = BlurEdgeTag(-1.0)
        t.normalize()
        assert t.value == 0.0

    def test_bold_weight_drops_below_100(self):
        t = BoldWeightTag(50)
        t.normalize()
        assert t.value is None

    def test_bold_weight_keeps_100_plus(self):
        t = BoldWeightTag(700)
        t.normalize()
        assert t.value == 700

    def test_wrap_style_out_of_range_drops(self):
        t = WrapStyleTag(9)
        t.normalize()
        assert t.value is None

    def test_wrap_style_in_range_keeps(self):
        for v in (1, 2, 3):
            t = WrapStyleTag(v)
            t.normalize()
            assert t.value == v

    def test_fontsize_absolute_negative_drops(self):
        t = FontSizeAbsoluteTag(-5.0)
        t.normalize()
        assert t.value is None

    def test_scale_x_clamps_negative(self):
        t = ScaleXTag(-10.0)
        t.normalize()
        assert t.value == 0.0

    def test_drawing_mode_clamps_negative(self):
        t = DrawingModeTag(-1)
        t.normalize()
        assert t.value == 0

    def test_base_normalize_is_noop(self):
        t = ResetStyleTag("Default")
        t.normalize()
        assert t.value == "Default"


class TestFromRawStrict:
    def test_strict_rejects_multi_params(self):
        with pytest.raises(ValueError):
            BorderTag.from_raw(
                RawTag("bord", ("1", "2"), "\\bord1,2", BorderTag), strict=True
            )

    def test_non_strict_takes_first_param(self):
        t = BorderTag.from_raw(RawTag("bord", ("1", "2"), "\\bord1,2", BorderTag))
        assert t.value == 1.0

    def test_invalid_param_falls_back_to_none(self):
        t = BorderTag.from_raw(RawTag("bord", ("abc",), "\\bordabc", BorderTag))
        assert t.value is None

    def test_no_params_returns_none_value(self):
        t = BorderTag.from_raw(RawTag("bord", (), "\\bord", BorderTag))
        assert t.value is None

    def test_position_strict_rejects_wrong_count(self):
        with pytest.raises(ValueError):
            PositionTag.from_raw(
                RawTag("pos", ("1",), "\\pos(1)", PositionTag), strict=True
            )

    def test_position_wrong_count_raises(self):
        with pytest.raises(ValueError):
            PositionTag.from_raw(RawTag("pos", ("1",), "\\pos(1)", PositionTag))

    def test_move_wrong_count_raises(self):
        with pytest.raises(ValueError):
            MoveTag.from_raw(
                RawTag("move", ("0", "0", "100"), "\\move(0,0,100)", MoveTag)
            )

    def test_fade_wrong_count_raises(self):
        with pytest.raises(ValueError):
            from light_ass.curly.tags import FadeTag

            FadeTag.from_raw(RawTag("fad", ("300",), "\\fad(300)", FadeTag))


class TestScaleTag:
    def test_no_value_serialize(self):
        t = ScaleTag.from_raw(RawTag("fsc", (), "\\fsc", ScaleTag))
        assert t.to_ass() == "\\fsc"

    def test_get_params(self):
        assert ScaleTag().get_params() == {"value": None}

    def test_parse_param_raises(self):
        with pytest.raises(ValueError):
            ScaleTag._parse_param("1")


class TestBoldDispatch:
    def test_bool_value_dispatches_to_simple(self):
        t = BoldTag.from_raw(RawTag("b", ("1",), "\\b1", BoldTag))
        assert isinstance(t, BoldSimpleTag)
        assert t.value is True

    def test_weight_dispatches_to_weight(self):
        t = BoldTag.from_raw(RawTag("b", ("700",), "\\b700", BoldTag))
        assert isinstance(t, BoldWeightTag)
        assert t.value == 700

    def test_zero_dispatches_to_simple(self):
        t = BoldTag.from_raw(RawTag("b", ("0",), "\\b0", BoldTag))
        assert isinstance(t, BoldSimpleTag)
        assert t.value is False

    def test_no_param_dispatches_to_simple(self):
        t = BoldTag.from_raw(RawTag("b", (), "\\b", BoldTag))
        assert isinstance(t, BoldSimpleTag)
        assert t.value is None


class TestAlignmentLegacyValues:
    def test_legacy_values_stable(self):
        from light_ass.curly.tags import LegacyAlignmentTag

        for v in range(1, 10):
            t = LegacyAlignmentTag.from_raw(
                RawTag("a", (str(v),), f"\\a{v}", LegacyAlignmentTag)
            )
            assert t.value is not None
            assert isinstance(t.value, Align)

    def test_legacy_a1_maps_to_bottom_left(self):
        from light_ass.curly.tags import LegacyAlignmentTag

        t = LegacyAlignmentTag.from_raw(
            RawTag("a", ("1",), "\\a1", LegacyAlignmentTag)
        )
        assert t.value == Align(1)

    def test_legacy_setter_int_coercion(self):
        from light_ass.curly.tags import LegacyAlignmentTag

        t = LegacyAlignmentTag(Align(1))
        t.value = 7
        assert t.value == Align.from_legacy(7)

    def test_alignment_value_int_coercion(self):
        from light_ass.curly.tags import AlignmentTag

        t = AlignmentTag(5)
        assert t.value == Align(5)

    def test_alignment_setter_int_coercion(self):
        from light_ass.curly.tags import AlignmentTag

        t = AlignmentTag(Align(1))
        t.value = 7
        assert t.value == Align(7)


class TestEffectGroup:
    def test_eq_same(self):
        assert EffectGroup("x", FirstPolicy) == EffectGroup("x", FirstPolicy)

    def test_eq_diff_policy(self):
        assert EffectGroup("x", FirstPolicy) != EffectGroup("x", OverridePolicy)

    def test_hash_same(self):
        assert hash(EffectGroup("x", FirstPolicy)) == hash(EffectGroup("x", FirstPolicy))

    def test_hash_in_dict(self):
        d: dict[EffectGroup, int] = {}
        d[EffectGroup("x", FirstPolicy)] = 1
        assert d[EffectGroup("x", FirstPolicy)] == 1

    def test_default_policy(self):
        assert EffectGroup("x").policy is OverridePolicy

    def test_frozen_cannot_set_attr(self):
        eg = EffectGroup("x", FirstPolicy)
        with pytest.raises((AttributeError, Exception)):
            eg.name = "y"  # type: ignore[misc]


class TestOverrideBlockSimplify:
    def test_override_policy_keeps_last(self):
        parser = TagParser()
        ob = parser.parse_block(r"\bord1\bord2\bord3")
        ob.simplify()
        tags = list(ob)
        assert len(tags) == 1
        assert tags[0].to_ass() == "\\bord3"

    def test_first_policy_keeps_first(self):
        parser = TagParser()
        ob = parser.parse_block(r"\pos(1,1)\pos(2,2)\pos(3,3)")
        ob.simplify()
        tags = list(ob)
        assert len(tags) == 1
        assert tags[0].to_ass() == "\\pos(1,1)"

    def test_different_effect_groups_all_kept(self):
        parser = TagParser()
        ob = parser.parse_block(r"\bord1\pos(1,1)")
        ob.simplify()
        assert len(list(ob)) == 2

    def test_get_effective_returns_correct_tag(self):
        parser = TagParser()
        ob = parser.parse_block(r"\an5\an8")
        effective = ob.get_effective("alignment")
        assert len(effective) == 1

    def test_get_effective_empty(self):
        parser = TagParser()
        ob = parser.parse_block(r"\bord1")
        assert ob.get_effective("alignment") == []


class TestParsedLineEffective:
    def test_get_effective_across_blocks(self):
        parser = TagParser()
        pl = parser.parse(r"{\an5}a{\an8}b")
        effective = pl.get_effective("alignment")
        assert len(effective) == 1

    def test_get_effective_position(self):
        parser = TagParser()
        pl = parser.parse(r"{\pos(10,20)}text{\pos(30,40)}")
        effective = pl.get_effective("position")
        assert len(effective) == 1
        assert effective[0].to_ass() == "\\pos(10,20)"


class TestParsedLineSimplify:
    def test_simplify_removes_overridden(self):
        parser = TagParser()
        pl = parser.parse(r"{\bord1\bord2}text")
        pl.simplify()

        blocks = [p for p in pl.parts if isinstance(p, OverrideBlock)]
        assert len(list(blocks[0])) == 1

    def test_simplify_keeps_text(self):
        parser = TagParser()
        pl = parser.parse(r"{\bord1\bord2}hello")
        pl.simplify()
        assert "hello" in pl.to_ass()


class TestRawTag:
    def test_eq(self):
        assert RawTag("b", ("1",), "\\b1", None) == RawTag("b", ("1",), "\\b1", None)

    def test_eq_ignores_cls(self):
        assert RawTag("b", ("1",), "\\b1", BorderTag) == RawTag(
            "b", ("1",), "\\b1", None
        )

    def test_eq_diff_name(self):
        assert RawTag("b", ("1",), "\\b1", None) != RawTag("i", ("1",), "\\i1", None)

    def test_eq_diff_params(self):
        assert RawTag("b", ("1",), "\\b1", None) != RawTag("b", ("2",), "\\b2", None)

    def test_eq_diff_raw_str(self):
        assert RawTag("b", ("1",), "\\b1", None) != RawTag("b", ("1",), "\\b2", None)

    def test_to_ass(self):
        assert RawTag("b", ("1",), "\\b1", None).to_ass() == "\\b1"

    def test_repr(self):
        r = repr(RawTag("b", ("1",), "\\b1", None))
        assert "b" in r and "\\b1" in r
