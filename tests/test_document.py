
from light_ass import Document, Events, ScriptInfo, Style, Styles

SAMPLE_ASS = """[Script Info]
Title: Test Script
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,48,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1
Style: Alt,Times New Roman,72,&H0000FFFF,&H00FF0000,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,3,3,2,20,20,20,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:05.00,Default,,0,0,0,,Hello World
Dialogue: 0,0:00:05.00,0:00:10.00,Alt,,0,0,0,,{\\b1}Second line{\\b0}
"""


class TestDocumentInit:
    def test_empty_default(self):
        doc = Document()
        assert isinstance(doc.info, ScriptInfo)
        assert isinstance(doc.styles, Styles)
        assert isinstance(doc.events, Events)
        assert len(doc.events) == 0

    def test_with_sections(self):
        info = ScriptInfo({"Title": "Test"})
        styles = Styles([Style(name="Default")])
        events = Events([])
        doc = Document(info=info, styles=styles, events=events)
        assert doc.info["Title"] == "Test"
        assert "Default" in doc.styles


class TestDocumentFromString:
    def test_load_full(self):
        doc = Document.from_string(SAMPLE_ASS)
        assert doc.info["Title"] == "Test Script"
        assert doc.info["PlayResX"] == 1920
        assert doc.info["PlayResY"] == 1080
        assert doc.info["ScaledBorderAndShadow"] is True
        assert len(doc.styles) == 2
        assert len(doc.events) == 2

    def test_events_text(self):
        doc = Document.from_string(SAMPLE_ASS)
        events = list(doc.events)
        assert events[0].text == "Hello World"
        assert events[1].text == "{\\b1}Second line{\\b0}"

    def test_strict_mode(self):
        doc = Document.from_string(SAMPLE_ASS, strict=True)
        assert len(doc.events) == 2

    def test_drop_unknown_sections(self):
        text = (
            "[Unknown Section]\n"
            "Key: Value\n\n"
            "[Script Info]\n"
            "Title: Test\n\n"
            "[Events]\n"
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
            "Dialogue: 0,0:00:00.00,0:00:05.00,Default,,0,0,0,,Hello"
        )
        doc = Document.from_string(text, drop_unknown_sections=True)
        assert len(doc.unknown_sections) == 0

    def test_keep_unknown_sections(self):
        text = "[Custom]\nData: value\n\n[Script Info]\nTitle: Test\n"
        doc = Document.from_string(text, drop_unknown_sections=False)
        assert "Custom" in doc.unknown_sections

    def test_empty_string(self):
        doc = Document.from_string("")
        assert len(doc.events) == 0
        assert len(doc.styles) == 0


class TestDocumentToAss:
    def test_round_trip(self):
        doc = Document.from_string(SAMPLE_ASS)
        result = doc.to_ass()
        assert "Script Info" in result
        assert "V4+ Styles" in result
        assert "Events" in result
        assert "Hello World" in result

    def test_custom_section_order(self):
        doc = Document.from_string(SAMPLE_ASS)
        result = doc.to_ass()
        idx_info = result.index("[Script Info]")
        idx_styles = result.index("[V4+ Styles]")
        idx_events = result.index("[Events]")
        assert idx_info < idx_styles < idx_events

    def test_default_section_order(self):
        doc = Document()
        result = doc.to_ass()
        idx_info = result.index("[Script Info]")
        idx_styles = result.index("[V4+ Styles]")
        idx_events = result.index("[Events]")
        assert idx_info < idx_styles < idx_events


class TestDocumentCopy:
    def test_copy_is_independent(self):
        doc = Document.from_string(SAMPLE_ASS)
        doc2 = doc.copy()
        doc2.info["Title"] = "Changed"
        assert doc.info["Title"] == "Test Script"
        assert doc2.info["Title"] == "Changed"

    def test_copy_events_independent(self):
        doc = Document.from_string(SAMPLE_ASS)
        doc2 = doc.copy()
        doc2.events[0].text = "Changed"
        assert doc.events[0].text == "Hello World"
        assert doc2.events[0].text == "Changed"


class TestDocumentRenameStyle:
    def test_rename_style_in_styles(self):
        doc = Document.from_string(SAMPLE_ASS)
        doc.rename_style("Default", "Primary")
        assert "Default" not in doc.styles
        assert "Primary" in doc.styles

    def test_rename_style_in_events(self):
        doc = Document.from_string(SAMPLE_ASS)
        doc.rename_style("Default", "Primary")
        assert doc.events[0].style == "Primary"

    def test_rename_style_in_tags(self):
        text = (
            "[Script Info]\nTitle: Test\n\n"
            "[V4+ Styles]\n"
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
            "Style: A,Arial,48,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1\n"
            "Style: B,Arial,48,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1\n\n"
            "[Events]\n"
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
            "Dialogue: 0,0:00:00.00,0:00:05.00,A,,0,0,0,,{\\rB}text"
        )
        doc = Document.from_string(text)
        doc.rename_style("B", "NewB")
        assert doc.events[0].style == "A"
        assert "NewB" in doc.events[0].text


class TestDocumentResample:
    def test_resample_up(self):
        text = (
            "[Script Info]\n"
            "PlayResX: 640\n"
            "PlayResY: 480\n\n"
            "[V4+ Styles]\n"
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
            "Style: Default,Arial,24,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1\n\n"
            "[Events]\n"
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
            "Dialogue: 0,0:00:00.00,0:00:05.00,Default,,0,0,0,,Test"
        )
        doc = Document.from_string(text)
        doc.resample(1280, 720)
        assert doc.info["PlayResX"] == 1280
        assert doc.info["PlayResY"] == 720
        style = doc.styles["Default"]
        assert style.fontsize == 48.0
        assert style.margin_l == 20
        assert style.margin_r == 20
        assert style.margin_v == 15

    def test_resample_same_resolution(self):
        text = (
            "[Script Info]\n"
            "PlayResX: 1920\n"
            "PlayResY: 1080\n\n"
            "[V4+ Styles]\n"
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
            "Style: Default,Arial,48,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1\n\n"
            "[Events]\n"
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
            "Dialogue: 0,0:00:00.00,0:00:05.00,Default,,0,0,0,,Test"
        )
        doc = Document.from_string(text)
        doc.resample(1920, 1080)
        style = doc.styles["Default"]
        assert style.fontsize == 48.0

    def test_resample_scale_tags(self):
        text = (
            "[Script Info]\n"
            "PlayResX: 640\n"
            "PlayResY: 480\n\n"
            "[V4+ Styles]\n"
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
            "Style: Default,Arial,20,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,1,0,2,10,10,10,1\n\n"
            "[Events]\n"
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
            "Dialogue: 0,0:00:00.00,0:00:05.00,Default,,0,0,0,,{\\fs32}{\\bord2}{\\shad1}{\\pos(160,120)}Tagged text"
        )
        doc = Document.from_string(text)
        doc.resample(1280, 720)
        assert doc.styles["Default"].fontsize > 20
        assert "pos" in doc.events[0].text

    def test_resample_clip_tags(self):
        text = (
            "[Script Info]\n"
            "PlayResX: 640\n"
            "PlayResY: 480\n\n"
            "[V4+ Styles]\n"
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
            "Style: Default,Arial,20,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,1,0,2,10,10,10,1\n\n"
            "[Events]\n"
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
            "Dialogue: 0,0:00:00.00,0:00:05.00,Default,,0,0,0,,{\\clip(0,0,320,240)}Clipped"
        )
        doc = Document.from_string(text)
        doc.resample(1280, 720)


class TestDocumentRepr:
    def test_repr(self):
        doc = Document.from_string(SAMPLE_ASS)
        assert "2 events" in repr(doc)

    def test_repr_empty(self):
        doc = Document()
        assert "0 events" in repr(doc)


class TestDocumentSectionParsers:
    def test_custom_parser(self):
        class MySection:
            SECTION_NAME = "Mysection"

            def __init__(self):
                self.data = {}

            @classmethod
            def from_ass(cls, text, strict=False):
                instance = cls()
                for line in text.splitlines():
                    k, _, v = line.partition(":")
                    instance.data[k.strip()] = v.strip()
                return instance

            def to_ass(self):
                return "\n".join(f"{k}: {v}" for k, v in self.data.items())

        text = "[Mysection]\nKey: Value\n\n[Script Info]\nTitle: Test\n"

        doc = Document.from_string(text, extra_sections=[MySection])
        assert "Mysection" in doc.section_results
        assert doc.section_results["Mysection"].data["Key"] == "Value"

    def test_custom_section_in_output(self):
        class MySection:
            SECTION_NAME = "Mysection"

            @classmethod
            def from_ass(cls, text, strict=False):
                return cls()

            def to_ass(self):
                return "Custom data"

        doc = Document()
        doc.section_order = ["Mysection"]
        doc.section_results["Mysection"] = MySection()
        doc.info["Title"] = "Test"

        result = doc.to_ass()
        assert "[Mysection]" in result
        assert "Custom data" in result
