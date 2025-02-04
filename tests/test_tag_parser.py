import unittest

from light_ass import tag_parser


class TestTagParser(unittest.TestCase):
    def test_tag_parser(self):
        text = r"123{\r\fn0\fs80\t(1,2,\t())}Lorem {ASS}ipsum{}\{明日はきっと天気で}"
        parsed = tag_parser.parse_tags(text)

        self.assertEqual(parsed[0].name, "Text")
        self.assertEqual(parsed[0].to_string(), "123")
        self.assertTrue(parsed[0].valid)

        self.assertEqual(parsed[1].name, "r")
        self.assertEqual(parsed[1].to_string(), r"\r")
        self.assertTrue(parsed[1].valid)

        self.assertEqual(parsed[2].name, "fn")
        self.assertEqual(parsed[2].to_string(), r"\fn")
        self.assertTrue(parsed[2].valid)

        self.assertEqual(parsed[3].name, "fs")
        self.assertEqual(parsed[3].to_string(), r"\fs80")
        self.assertTrue(parsed[3].valid)

        self.assertEqual(parsed[4].name, "t")
        self.assertEqual(parsed[4].to_string(), r"\t(1,2,\t)")
        self.assertTrue(parsed[4].valid)
        self.assertFalse(parsed[4].args[-1][0].valid)

        self.assertEqual(parsed[7].name, "Comment")
        self.assertEqual(parsed[7].to_string(), r"ASS")
        self.assertTrue(parsed[7].valid)

        self.assertEqual(parsed[9].name, "Text")
        self.assertEqual(parsed[9].to_string(), r"\{明日はきっと天気で}")
        self.assertTrue(parsed[9].valid)

        self.assertEqual(tag_parser.join_tags(parsed, skip_comment=True),
                         r"123{\r\fn\fs80\t(1,2,\t)}Lorem ipsum\{明日はきっと天気で}")

        text = r"{\move(2,3,4,5)\t(1,2,\move(2,3,4,5)}"
        parsed = tag_parser.parse_tags(text)
        self.assertEqual(parsed[0].name, "move")
        self.assertEqual(parsed[0].to_string(), r"\move(2,3,4,5)")
        self.assertTrue(parsed[0].valid)
        self.assertEqual(parsed[1].name, "t")
        self.assertEqual(parsed[1].to_string(), r"\t(1,2,\move(2,3,4,5))")
        self.assertTrue(parsed[1].valid)
