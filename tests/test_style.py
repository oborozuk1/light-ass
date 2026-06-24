import pytest

from light_ass import AssAlpha, AssColor, Style


class TestStyleInit:
    def test_defaults(self):
        s = Style(name="Test")
        assert s.name == "Test"
        assert s.fontname == "Arial"
        assert s.fontsize == 48.0
        assert s.bold is False
        assert s.italic is False
        assert s.underline is False
        assert s.strike_out is False
        assert s.scale_x == 100.0
        assert s.scale_y == 100.0
        assert s.spacing == 0.0
        assert s.angle == 0.0
        assert s.border_style == 1
        assert s.outline == 2.0
        assert s.shadow == 2.0
        assert s.alignment == 2
        assert s.margin_l == 10
        assert s.margin_r == 10
        assert s.margin_v == 10
        assert s.encoding == 1

    def test_default_colors(self):
        s = Style(name="Test")
        assert s.primary_colour == AssColor(255, 255, 255)
        assert s.secondary_colour == AssColor(255, 0, 0)
        assert s.outline_colour == AssColor(0, 0, 0)
        assert s.back_colour == AssColor(0, 0, 0)

    def test_default_alphas(self):
        s = Style(name="Test")
        assert s.primary_alpha == AssAlpha(0)
        assert s.secondary_alpha == AssAlpha(0)
        assert s.outline_alpha == AssAlpha(0)
        assert s.back_alpha == AssAlpha(0)


class TestStyleColorProperties:
    def test_color_properties(self):
        s = Style(name="Test")
        c = AssColor(100, 150, 200)
        s.color1 = c
        assert s.primary_colour == c
        s.color2 = c
        assert s.secondary_colour == c
        s.color3 = c
        assert s.outline_colour == c
        s.color4 = c
        assert s.back_colour == c

    def test_alpha_properties(self):
        s = Style(name="Test")
        a = AssAlpha(128)
        s.alpha1 = a
        assert s.primary_alpha == a
        s.alpha2 = a
        assert s.secondary_alpha == a
        s.alpha3 = a
        assert s.outline_alpha == a
        s.alpha4 = a
        assert s.back_alpha == a

    def test_color1_get(self):
        s = Style(name="Test")
        assert s.color1 == s.primary_colour

    def test_color2_get(self):
        s = Style(name="Test")
        assert s.color2 == s.secondary_colour

    def test_color3_get(self):
        s = Style(name="Test")
        assert s.color3 == s.outline_colour

    def test_color4_get(self):
        s = Style(name="Test")
        assert s.color4 == s.back_colour


class TestStyleFromAss:
    def test_basic_style(self):
        line = "Style: Default,Arial,48,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1"
        s = Style.from_ass(line)
        assert s.name == "Default"
        assert s.fontname == "Arial"
        assert s.fontsize == 48.0
        assert s.primary_colour == AssColor(255, 255, 255)
        assert s.primary_alpha == AssAlpha(0)
        assert s.secondary_colour == AssColor(255, 0, 0)
        assert s.secondary_alpha == AssAlpha(0)
        assert s.outline_colour == AssColor(0, 0, 0)
        assert s.outline_alpha == AssAlpha(0)
        assert s.back_colour == AssColor(0, 0, 0)
        assert s.back_alpha == AssAlpha(0)
        assert s.bold is False
        assert s.italic is False
        assert s.underline is False
        assert s.strike_out is False
        assert s.scale_x == 100.0
        assert s.scale_y == 100.0
        assert s.border_style == 1
        assert s.outline == 2.0
        assert s.shadow == 2.0
        assert s.alignment == 2

    def test_with_alpha(self):
        line = "Style: Test,Arial,48,&H80FF0000,&H00000000,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,2,10,10,10,1"
        s = Style.from_ass(line)
        assert s.primary_colour == AssColor(0, 0, 255)
        assert s.primary_alpha == AssAlpha(0x80)

    def test_starred_name(self):
        line = "Style: *Default,Arial,48,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1"
        s = Style.from_ass(line)
        assert s.name == "Default"

    def test_empty_name_raises(self):
        line = "Style: ,Arial,48,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1"
        with pytest.raises(ValueError):
            Style.from_ass(line)

    def test_custom_format_order(self):
        fmt = (
            "Name",
            "Fontname",
            "Fontsize",
            "PrimaryColour",
            "SecondaryColour",
            "OutlineColour",
            "BackColour",
            "Bold",
            "Italic",
            "Underline",
            "StrikeOut",
            "ScaleX",
            "ScaleY",
            "Spacing",
            "Angle",
            "BorderStyle",
            "Outline",
            "Shadow",
            "Alignment",
            "MarginL",
            "MarginR",
            "MarginV",
            "Encoding",
        )
        line = "Style: MyStyle,Times,72,&H000000FF,&H0000FF00,&H00FF0000,&H00000000,1,0,0,0,100,100,0,0,2,5,3,5,20,20,20,1"
        s = Style.from_ass(line, fmt)
        assert s.name == "MyStyle"
        assert s.fontname == "Times"
        assert s.fontsize == 72.0
        assert s.bold is True


class TestStyleToAss:
    def test_default_style(self):
        s = Style(name="Default")
        result = s.to_ass()
        assert result.startswith("Style: Default")
        assert "Arial" in result
        assert "48" in result

    def test_round_trip(self):
        original = "Style: Test,Arial,48,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1"
        s = Style.from_ass(original)
        result = s.to_ass()
        assert "Style: Test" in result
        assert "48" in result

    def test_bold_in_tostring(self):
        s = Style(name="Bold", bold=True)
        result = s.to_ass()
        assert "-1" in result


class TestStyleFormatColor:
    def test_format_color(self):
        s = Style(name="Test")
        result = s._format_alpha_color(AssColor(0, 255, 0), AssAlpha(0x80))
        assert result == "&H8000FF00"
