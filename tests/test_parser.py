import unittest

from light_ass import Subtitle

class TestParser(unittest.TestCase):
    def test_from_file(self):
        doc = Subtitle.load("test1.ass")

        self.assertEqual(doc.info["PlayResX"], 500)
        self.assertEqual(doc.info["PlayResY"], 600)
        self.assertEqual(doc.info["LayoutResX"], 500)
        self.assertEqual(doc.info["LayoutResY"], 600)
        self.assertEqual(doc.info["ScriptType"], "v4.00+")

        self.assertEqual(doc.styles["Default"].fontname, "Arial")
        self.assertEqual(doc.styles["Default"].fontsize, 20)
        self.assertEqual(str(doc.styles["Default"]), "Style: Default,Arial,20,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,1,2,5,10,10,10,1")

        self.assertEqual(len(doc.events), 5)
        self.assertEqual(doc.events[0].start, 0)
        self.assertEqual(doc.events[0].end_time, 5000)
        self.assertEqual(doc.events[0].text, r"{\3c&H0000FF}this is a test\N{\3c&H00FF00}this is a test\N{\3c&HFF0000}this is a test")
        self.assertEqual(doc.events[0].text_stripped, r"this is a test\Nthis is a test\Nthis is a test")
        self.assertEqual(doc.events[1].text, r"{\an2}this is a line at \an2")
        self.assertTrue(doc.events[1].comment)
        self.assertEqual(doc.events[2].text_stripped, r"this \{Comment}is a line at \an8{")