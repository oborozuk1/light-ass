import pytest

from light_ass.curly.tags.base import RawTag
from light_ass.curly.tags.parens import (
    ClipRectTag,
    ClipShapeTag,
    ClipTag,
    FadeComplexTag,
    FadeSimpleTag,
    FadeTag,
    InverseClipRectTag,
    InverseClipShapeTag,
    InverseClipTag,
    MoveTag,
    OriginTag,
    PositionTag,
)
from light_ass.types import AssShape


class TestPositionTag:
    def test_from_raw(self):
        t = PositionTag.from_raw(RawTag("pos", ("100", "200"), "\\pos(100,200)", PositionTag))
        assert t.x == 100
        assert t.y == 200

    def test_serialize(self):
        t = PositionTag(100, 200)
        assert t.to_ass() == "\\pos(100,200)"

    def test_serialize_float(self):
        t = PositionTag(1.5, 2.5)
        assert "1.5" in t.to_ass()
        assert "2.5" in t.to_ass()

    def test_invalid_param_count(self):
        with pytest.raises(ValueError):
            PositionTag.from_raw(RawTag("pos", ("100",), "\\pos(100)", PositionTag))

    def test_get_params(self):
        t = PositionTag(10, 20)
        assert t.get_params() == (10, 20)


class TestMoveTag:
    def test_four_params(self):
        t = MoveTag.from_raw(
            RawTag("move", ("0", "0", "100", "200"), "\\move(0,0,100,200)", MoveTag)
        )
        assert t.x1 == 0
        assert t.y1 == 0
        assert t.x2 == 100
        assert t.y2 == 200
        assert t.t1 is None
        assert t.t2 is None

    def test_six_params(self):
        t = MoveTag.from_raw(
            RawTag(
                "move",
                ("0", "0", "100", "200", "500", "1000"),
                "\\move(0,0,100,200,500,1000)",
                MoveTag,
            )
        )
        assert t.x1 == 0
        assert t.y1 == 0
        assert t.x2 == 100
        assert t.y2 == 200
        assert t.t1 == 500
        assert t.t2 == 1000

    def test_serialize_four(self):
        t = MoveTag(0, 0, 100, 200)
        assert t.to_ass() == "\\move(0,0,100,200)"

    def test_serialize_six(self):
        t = MoveTag(0, 0, 100, 200, 500, 1000)
        result = t.to_ass()
        assert "500" in result
        assert "1000" in result

    def test_invalid_param_count(self):
        with pytest.raises(ValueError):
            MoveTag.from_raw(RawTag("move", ("0", "0", "100"), "\\move(0,0,100)", MoveTag))


class TestClipTag:
    def test_rect_four_params(self):
        t = ClipTag.from_raw(
            RawTag("clip", ("10", "20", "30", "40"), "\\clip(10,20,30,40)", ClipTag)
        )
        assert isinstance(t, ClipRectTag)
        assert t.x1 == 10
        assert t.y1 == 20
        assert t.x2 == 30
        assert t.y2 == 40

    def test_shape_one_param(self):
        t = ClipTag.from_raw(RawTag("clip", ("m 0 0 l 10 10",), "\\clip(m 0 0 l 10 10)", ClipTag))
        assert isinstance(t, ClipShapeTag)

    def test_shape_two_params(self):
        t = ClipTag.from_raw(
            RawTag("clip", ("2", "m 0 0 l 10 10"), "\\clip(2,m 0 0 l 10 10)", ClipTag)
        )
        assert isinstance(t, ClipShapeTag)
        assert t.scale == 2

    def test_rect_serialize(self):
        t = ClipRectTag(10, 20, 30, 40)
        assert t.to_ass() == "\\clip(10,20,30,40)"

    def test_rect_get_params(self):
        t = ClipRectTag(10, 20, 30, 40)
        assert t.get_params() == (10, 20, 30, 40)


class TestInverseClipTag:
    def test_rect_four_params(self):
        t = InverseClipTag.from_raw(
            RawTag("iclip", ("0", "0", "100", "200"), "\\iclip(0,0,100,200)", InverseClipTag)
        )
        assert isinstance(t, InverseClipRectTag)
        assert t.x1 == 0
        assert t.x2 == 100

    def test_shape(self):
        t = InverseClipTag.from_raw(
            RawTag("iclip", ("m 0 0 l 10 10",), "\\iclip(m 0 0 l 10 10)", InverseClipTag)
        )
        assert isinstance(t, InverseClipShapeTag)

    def test_rect_serialize(self):
        t = InverseClipRectTag(0, 0, 100, 200)
        assert t.to_ass() == "\\iclip(0,0,100,200)"


class TestFadeTag:
    def test_simple_fade(self):
        t = FadeTag.from_raw(RawTag("fad", ("300", "500"), "\\fad(300,500)", FadeTag))
        assert isinstance(t, FadeSimpleTag)
        assert t.fade_in == 300
        assert t.fade_out == 500

    def test_complex_fade(self):
        t = FadeTag.from_raw(
            RawTag(
                "fade",
                ("255", "128", "0", "0", "1000", "2000", "3000"),
                "\\fade(255,128,0,0,1000,2000,3000)",
                FadeTag,
            )
        )
        assert isinstance(t, FadeComplexTag)
        assert t.a1 == 255
        assert t.a2 == 128
        assert t.a3 == 0
        assert t.t1 == 0
        assert t.t2 == 1000
        assert t.t3 == 2000
        assert t.t4 == 3000

    def test_fade_alias(self):
        t = FadeTag.from_raw(RawTag("fade", ("300", "500"), "\\fade(300,500)", FadeTag))
        assert isinstance(t, FadeSimpleTag)

    def test_simple_serialize(self):
        t = FadeSimpleTag(300, 500)
        assert t.to_ass() == "\\fad(300,500)"

    def test_complex_serialize(self):
        t = FadeComplexTag(255, 128, 0, 0, 1000, 2000, 3000)
        assert t.to_ass() == "\\fade(255,128,0,0,1000,2000,3000)"

    def test_invalid_param_count(self):
        with pytest.raises(ValueError):
            FadeTag.from_raw(RawTag("fad", ("300",), "\\fad(300)", FadeTag))


class TestOriginTag:
    def test_from_raw(self):
        t = OriginTag.from_raw(RawTag("org", ("50", "100"), "\\org(50,100)", OriginTag))
        assert t.x == 50
        assert t.y == 100

    def test_serialize(self):
        t = OriginTag(50, 100)
        assert t.to_ass() == "\\org(50,100)"

    def test_invalid_param_count(self):
        with pytest.raises(ValueError):
            OriginTag.from_raw(RawTag("org", ("50",), "\\org(50)", OriginTag))


class TestClipShapeSerialization:
    def test_clip_shape_with_scale(self):
        shape = AssShape.from_ass("m 0 0 l 10 10")
        shape.commands
        t = ClipShapeTag(shape, 2)
        result = t.to_ass()
        assert "clip" in result

    def test_clip_shape_without_scale(self):
        shape = AssShape.from_ass("m 0 0 l 10 10")
        shape.commands
        t = ClipShapeTag(shape)
        result = t.to_ass()
        assert "clip" in result


class TestTransformTag:
    def test_from_raw_simple(self):
        from light_ass.curly.parser import TagParser
        from light_ass.curly.tags.base import RawTag
        from light_ass.curly.tags.transform import TransformTag

        parser = TagParser()
        t = TransformTag.from_raw(
            RawTag("t", ("\\b1",), "\\t(\\b1)", TransformTag),
            parser=parser,
        )
        assert len(t.modifier) > 0

    def test_transform_with_time(self):
        from light_ass.curly.parser import TagParser
        from light_ass.curly.tags.base import RawTag
        from light_ass.curly.tags.transform import TransformTag

        parser = TagParser()
        t = TransformTag.from_raw(
            RawTag("t", ("500", "1000", "0.5", "\\fs48"), "\\t(500,1000,0.5,\\fs48)", TransformTag),
            parser=parser,
        )
        assert t.t1 == 500
        assert t.t2 == 1000
        assert t.accel == 0.5
