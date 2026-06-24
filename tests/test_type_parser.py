import pytest

from light_ass.utils.type_parser import TypeParser, clamp


class TestClamp:
    def test_within_range(self):
        assert clamp(5, 0, 10) == 5

    def test_below_min(self):
        assert clamp(-5, 0, 10) == 0

    def test_above_max(self):
        assert clamp(15, 0, 10) == 10

    def test_at_min(self):
        assert clamp(0, 0, 10) == 0

    def test_at_max(self):
        assert clamp(10, 0, 10) == 10

    def test_float(self):
        assert clamp(5.5, 1.0, 10.0) == 5.5

    def test_float_above(self):
        assert clamp(15.0, 1.0, 10.0) == 10.0


class TestTypeParserParseInt:
    def test_positive(self):
        assert TypeParser.parse_int("42") == 42

    def test_negative(self):
        assert TypeParser.parse_int("-42") == -42

    def test_with_whitespace(self):
        assert TypeParser.parse_int("  42  ") == 42

    def test_with_trailing_text(self):
        assert TypeParser.parse_int("42abc") == 42

    def test_invalid_raises(self):
        with pytest.raises(ValueError):
            TypeParser.parse_int("abc")

    def test_zero(self):
        assert TypeParser.parse_int("0") == 0


class TestTypeParserParseFloat:
    def test_positive(self):
        assert TypeParser.parse_float("3.14") == pytest.approx(3.14)

    def test_negative(self):
        assert TypeParser.parse_float("-3.14") == pytest.approx(-3.14)

    def test_integer(self):
        assert TypeParser.parse_float("42") == 42.0

    def test_scientific(self):
        assert TypeParser.parse_float("1e3") == 1000.0

    def test_with_whitespace(self):
        assert TypeParser.parse_float("  3.14  ") == pytest.approx(3.14)

    def test_invalid_raises(self):
        with pytest.raises(ValueError):
            TypeParser.parse_float("abc")


class TestTypeParserParseBool:
    def test_true(self):
        assert TypeParser.parse_bool("1") is True

    def test_false(self):
        assert TypeParser.parse_bool("0") is False

    def test_invalid(self):
        with pytest.raises(ValueError):
            TypeParser.parse_bool("yes")

    def test_empty(self):
        with pytest.raises(ValueError):
            TypeParser.parse_bool("")


class TestTypeParserParseStr:
    def test_normal(self):
        assert TypeParser.parse_str("hello") == "hello"

    def test_leading_whitespace(self):
        assert TypeParser.parse_str("  hello") == "hello"

    def test_trailing_whitespace_kept(self):
        assert TypeParser.parse_str("hello  ") == "hello  "


class TestTypeParserHexToInt:
    def test_hex(self):
        assert TypeParser.hex_to_int("ff") == 255

    def test_hex_lowercase(self):
        assert TypeParser.hex_to_int("ff") == 255

    def test_hex_with_prefix(self):
        assert TypeParser.hex_to_int("0x") == 0

    def test_zero(self):
        assert TypeParser.hex_to_int("0") == 0

    def test_invalid(self):
        with pytest.raises(ValueError):
            TypeParser.hex_to_int("xyz")


class TestTypeParserIntToInt32:
    def test_normal(self):
        assert TypeParser.int_to_int32(100) == 100

    def test_above_max(self):
        assert TypeParser.int_to_int32(3_000_000_000) == 2_147_483_647

    def test_below_min(self):
        assert TypeParser.int_to_int32(-3_000_000_000) == -2_147_483_648


class TestTypeParserParseColor:
    def test_red(self):
        c = TypeParser.parse_color("&H0000FF&")
        assert c.r == 255
        assert c.g == 0
        assert c.b == 0

    def test_green(self):
        c = TypeParser.parse_color("&H00FF00&")
        assert c.r == 0
        assert c.g == 255
        assert c.b == 0

    def test_blue(self):
        c = TypeParser.parse_color("&HFF0000&")
        assert c.r == 0
        assert c.g == 0
        assert c.b == 255

    def test_lowercase(self):
        c = TypeParser.parse_color("&h00ff00&")
        assert c.g == 255


class TestTypeParserParseAlpha:
    def test_alpha(self):
        a = TypeParser.parse_alpha("&H80&")
        assert a.value == 0x80

    def test_alpha_ff(self):
        a = TypeParser.parse_alpha("&HFF&")
        assert a.value == 255

    def test_alpha_zero(self):
        a = TypeParser.parse_alpha("&H00&")
        assert a.value == 0

    def test_alpha_lowercase(self):
        a = TypeParser.parse_alpha("&hff&")
        assert a.value == 255
