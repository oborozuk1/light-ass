
from light_ass import AssColor


class TestAssColorFromAss:
    def test_red(self):
        c = AssColor.from_ass("&H0000FF&")
        assert c.r == 255
        assert c.g == 0
        assert c.b == 0

    def test_green(self):
        c = AssColor.from_ass("&H00FF00&")
        assert c.r == 0
        assert c.g == 255
        assert c.b == 0

    def test_blue(self):
        c = AssColor.from_ass("&HFF0000&")
        assert c.r == 0
        assert c.g == 0
        assert c.b == 255

    def test_white(self):
        c = AssColor.from_ass("&HFFFFFF&")
        assert c.r == 255
        assert c.g == 255
        assert c.b == 255

    def test_black(self):
        c = AssColor.from_ass("&H000000&")
        assert c.r == 0
        assert c.g == 0
        assert c.b == 0

    def test_mixed(self):
        c = AssColor.from_ass("&H123456&")
        assert c.r == 0x56
        assert c.g == 0x34
        assert c.b == 0x12

    def test_lowercase(self):
        c = AssColor.from_ass("&h00ff00&")
        assert c.g == 255

    def test_without_ampersand(self):
        c = AssColor.from_ass("0000FF")
        assert c.r == 255


class TestAssColorFromHex:
    def test_red(self):
        c = AssColor.from_hex("FF0000")
        assert c.r == 255
        assert c.g == 0
        assert c.b == 0

    def test_green(self):
        c = AssColor.from_hex("00FF00")
        assert c.r == 0
        assert c.g == 255
        assert c.b == 0

    def test_blue(self):
        c = AssColor.from_hex("0000FF")
        assert c.r == 0
        assert c.g == 0
        assert c.b == 255


class TestAssColorParse:
    def test_ass_format(self):
        c = AssColor.parse("&H00FF00&")
        assert c.g == 255

    def test_hex_hash(self):
        c = AssColor.from_hex("FF0000")
        assert c.r == 255
        assert c.g == 0
        assert c.b == 0

    def test_plain_hex(self):
        c = AssColor.parse("00FF00")
        assert c.g == 255


class TestAssColorFormat:
    def test_to_ass(self):
        c = AssColor(255, 0, 0)
        assert c.to_ass() == "&H0000FF"

    def test_to_ass_green(self):
        c = AssColor(0, 255, 0)
        assert c.to_ass() == "&H00FF00"

    def test_to_ass_blue(self):
        c = AssColor(0, 0, 255)
        assert c.to_ass() == "&HFF0000"

    def test_str(self):
        c = AssColor(0, 255, 0)
        assert str(c) == "&H00FF00"

    def test_format_custom(self):
        c = AssColor(0xFF, 0xAB, 0x55)
        result = c.format("{B}_{G}_{R}")
        assert result == "55_AB_FF"
