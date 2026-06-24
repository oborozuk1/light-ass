import pytest

from light_ass import Document


@pytest.fixture
def minimal_ass_text():
    return """[Script Info]
Title: Test
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,48,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:05.00,Default,,0,0,0,,Hello World
Dialogue: 0,0:00:05.00,0:00:10.00,Default,,0,0,0,,Second line
"""


@pytest.fixture
def empty_document():
    return Document()


@pytest.fixture
def sample_document(minimal_ass_text):
    return Document.from_string(minimal_ass_text)
