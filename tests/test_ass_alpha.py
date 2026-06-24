import pytest

from light_ass import AssAlpha


class TestAssAlphaParse:
    def test_parse_string(self):
        a = AssAlpha.parse("&H80&")
        assert a.value == 0x80

    def test_parse_string_lowercase(self):
        a = AssAlpha.parse("&hff&")
        assert a.value == 255

    def test_parse_int_zero(self):
        a = AssAlpha.parse(0)
        assert a.value == 0

    def test_parse_int_max(self):
        a = AssAlpha.parse(255)
        assert a.value == 255

    def test_parse_int_mid(self):
        a = AssAlpha.parse(128)
        assert a.value == 128

    def test_parse_int_out_of_range(self):
        with pytest.raises(ValueError):
            AssAlpha.parse(256)

    def test_parse_int_negative(self):
        with pytest.raises(ValueError):
            AssAlpha.parse(-1)

    def test_parse_without_ampersand(self):
        a = AssAlpha.parse("80")
        assert a.value == 0x80


class TestAssAlphaFormat:
    def test_to_ass(self):
        a = AssAlpha(0x80)
        assert a.to_ass() == "&H80&"

    def test_to_ass_ff(self):
        a = AssAlpha(255)
        assert a.to_ass() == "&HFF&"

    def test_hex_value(self):
        a = AssAlpha(0xAB)
        assert a.hex_value == "AB"

    def test_hex_value_padded(self):
        a = AssAlpha(5)
        assert a.hex_value == "05"

    def test_format_custom(self):
        a = AssAlpha(0x80)
        assert a.format("Alpha={A}") == "Alpha=80"
