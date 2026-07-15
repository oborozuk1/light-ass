
from light_ass.types import AssAlpha, AssColor
from light_ass.utils.formatter import Formatter


class TestFormatFloat:
    def test_integer(self):
        assert Formatter.format_float(5.0) == "5"

    def test_with_decimal(self):
        assert Formatter.format_float(3.14) == "3.14"

    def test_trailing_zeros(self):
        assert Formatter.format_float(3.1400) == "3.14"

    def test_strips_dot(self):
        assert Formatter.format_float(5.0) == "5"

    def test_custom_decimal(self):
        assert Formatter.format_float(3.14159, decimal=2) == "3.14"

    def test_negative(self):
        assert Formatter.format_float(-5.5) == "-5.5"

    def test_zero(self):
        assert Formatter.format_float(0.0) == "0"

    def test_small_fraction(self):
        assert Formatter.format_float(0.001) == "0.001"


class TestFormatDispatch:
    def test_float(self):
        assert Formatter.format(3.14) == "3.14"

    def test_bool_true(self):
        assert Formatter.format(True) == "1"

    def test_bool_false(self):
        assert Formatter.format(False) == "0"

    def test_ass_color(self):
        c = AssColor(255, 0, 0)
        assert Formatter.format(c) == "&H0000FF&"

    def test_ass_alpha(self):
        a = AssAlpha(0x80)
        assert Formatter.format(a) == "&H80&"

    def test_string(self):
        assert Formatter.format("hello") == "hello"

    def test_int(self):
        assert Formatter.format(42) == "42"
