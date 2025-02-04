import unittest

from light_ass import utils

class TestUtils(unittest.TestCase):
    def test_parse_int(self):
        self.assertEqual(utils.parse_int32("10"), 10)
        self.assertEqual(utils.parse_int32(" 0012"), 12)
        self.assertEqual(utils.parse_int32("10.a"), 10)
        self.assertEqual(utils.parse_int32("+80"), 80)
        self.assertEqual(utils.parse_int32("-100"), -100)
        self.assertEqual(utils.parse_int32("    -2"), -2)
        self.assertEqual(utils.parse_int32("   -6+"), -6)
        self.assertEqual(utils.parse_int32("+-6+"), 0)
        self.assertEqual(utils.parse_int32("1234567899999"), utils.INT32_MAX)
        self.assertEqual(utils.parse_int32("-1234567899999"), utils.INT32_MIN)

        self.assertEqual(utils.parse_positive_int32("10"), 10)
        self.assertEqual(utils.parse_positive_int32(" 0012"), 12)
        self.assertEqual(utils.parse_positive_int32("+-6+"), 0)
        self.assertEqual(utils.parse_positive_int32("-9"), 0)
        self.assertEqual(utils.parse_positive_int32("    -2"), 0)

    def test_parse_float(self):
        self.assertEqual(utils.parse_float("10"), 10.0)
        self.assertEqual(utils.parse_float("3.14"), 3.14)
        self.assertEqual(utils.parse_float(" 0.012"), 0.012)
        self.assertEqual(utils.parse_float("."), 0.0)
        self.assertEqual(utils.parse_float("-."), 0.0)
        self.assertEqual(utils.parse_float("+8.01.2"), 8.01)
        self.assertEqual(utils.parse_float("-1.00"), -1.0)
        self.assertEqual(utils.parse_float("    -.2"), -0.2)
        self.assertEqual(utils.parse_float("   -6+"), -6.0)
        self.assertEqual(utils.parse_float(" +6.a "), 6.0)
        self.assertEqual(utils.parse_float("+-6..+"), 0)

        self.assertEqual(utils.parse_positive_float("10"), 10.0)
        self.assertEqual(utils.parse_positive_float(" 0.012"), 0.012)
        self.assertEqual(utils.parse_positive_float("+-6+"), 0.0)
        self.assertEqual(utils.parse_positive_float("-9.15"), 0.0)
        self.assertEqual(utils.parse_positive_float("    -2.1"), 0.0)

    def test_parse_ass_color(self):
        self.assertEqual(utils.parse_ass_color("+12345").value, 0x45230100)
        self.assertEqual(utils.parse_ass_color(" &6666").value, 0x00000000)
        self.assertEqual(utils.parse_ass_color("+&589").value, 0x00000000)
        self.assertEqual(utils.parse_ass_color("FFFFFF").value, 0xFFFFFF00)
        self.assertEqual(utils.parse_ass_color("&H8FABCDEF&").value, 0xFFFFFF00)
        self.assertEqual(utils.parse_ass_color("&H5FABCDEF&").value, 0xEFCDAB00)

    def test_parse_ass_alpha(self):
        self.assertEqual(utils.parse_ass_alpha("86").value, 0x86)
        self.assertEqual(utils.parse_ass_alpha("& 82").value, 0x82)
        self.assertEqual(utils.parse_ass_alpha(" & 12").value, 0)
        self.assertEqual(utils.parse_ass_alpha("X").value, 0)
        self.assertEqual(utils.parse_ass_alpha("FDFD").value, 0xFD)