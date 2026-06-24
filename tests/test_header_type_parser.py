import pytest

from light_ass.types import AssTime
from light_ass.utils.header_type_parser import HeaderTypeParser


class TestHeaderTypeParserParseInt:
    def test_decimal(self):
        assert HeaderTypeParser.parse_int("42") == 42

    def test_hex_h_prefix(self):
        assert HeaderTypeParser.parse_int("&HFF") == 255

    def test_hex_0x_prefix(self):
        assert HeaderTypeParser.parse_int("0xFF") == 255

    def test_negative(self):
        assert HeaderTypeParser.parse_int("-10") == -10

    def test_invalid_returns_zero(self):
        assert HeaderTypeParser.parse_int("abc") == 0


class TestHeaderTypeParserParseFloat:
    def test_simple(self):
        assert HeaderTypeParser.parse_float("3.14") == pytest.approx(3.14)

    def test_integer(self):
        assert HeaderTypeParser.parse_float("10") == 10.0

    def test_negative(self):
        assert HeaderTypeParser.parse_float("-5.5") == pytest.approx(-5.5)


class TestHeaderTypeParserParseBool:
    def test_yes(self):
        assert HeaderTypeParser.parse_bool("yes") is True

    def test_no(self):
        assert HeaderTypeParser.parse_bool("no") is False

    def test_positive_int(self):
        assert HeaderTypeParser.parse_bool("1") is True

    def test_zero(self):
        assert HeaderTypeParser.parse_bool("0") is False

    def test_random_string(self):
        assert HeaderTypeParser.parse_bool("xyz") is False


class TestHeaderTypeParserParseStr:
    def test_normal(self):
        assert HeaderTypeParser.parse_str("hello") == "hello"

    def test_leading_whitespace(self):
        assert HeaderTypeParser.parse_str("  hello") == "hello"


class TestHeaderTypeParserParseStarredStr:
    def test_normal(self):
        assert HeaderTypeParser.parse_starred_str("hello") == "hello"

    def test_with_star(self):
        assert HeaderTypeParser.parse_starred_str("*Default") == "Default"

    def test_whitespace_and_star(self):
        assert HeaderTypeParser.parse_starred_str("  *Default") == "Default"


class TestHeaderTypeParserParseTime:
    def test_simple(self):
        t = HeaderTypeParser.parse_time("0:00:05.00")
        assert isinstance(t, AssTime)
        assert t.time == 5000

    def test_large(self):
        t = HeaderTypeParser.parse_time("1:30:00.00")
        assert t.time == 5400000


class TestHeaderTypeParserParseColorWithAlpha:
    def test_full(self):
        color, alpha = HeaderTypeParser.parse_color_with_alpha("&H80FF0000&")
        assert color.r == 0
        assert color.g == 0
        assert color.b == 255
        assert alpha.value == 0x80

    def test_no_alpha(self):
        color, alpha = HeaderTypeParser.parse_color_with_alpha("&H0000FF00&")
        assert color.g == 255
        assert alpha.value == 0

    def test_lowercase(self):
        color, alpha = HeaderTypeParser.parse_color_with_alpha("&h40ffffff&")
        assert color.r == 255
        assert color.g == 255
        assert color.b == 255
        assert alpha.value == 0x40


class TestHeaderTypeParserParseYCbCrMatrix:
    def test_bt601_tv(self):
        from light_ass.constants import YCbCrMatrix

        result = HeaderTypeParser.parse_ycbcr_matrix("TV.601")
        assert result == YCbCrMatrix.BT601_TV

    def test_bt709_pc(self):
        from light_ass.constants import YCbCrMatrix

        result = HeaderTypeParser.parse_ycbcr_matrix("PC.709")
        assert result == YCbCrMatrix.BT709_PC

    def test_none_matrix(self):
        from light_ass.constants import YCbCrMatrix

        result = HeaderTypeParser.parse_ycbcr_matrix("NONE")
        assert result == YCbCrMatrix.NONE

    def test_unknown_returns_string(self):
        result = HeaderTypeParser.parse_ycbcr_matrix("UNKNOWN")
        assert result == "UNKNOWN"
