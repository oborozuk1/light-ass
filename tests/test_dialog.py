import pytest

from light_ass import AssTime, Dialog


class TestDialogInit:
    def test_defaults(self):
        d = Dialog(text="Hello")
        assert d.text == "Hello"
        assert d.comment is False
        assert d.layer == 0
        assert d.start == AssTime(0)
        assert d.end == AssTime(0)
        assert d.style == "Default"
        assert d.name == ""
        assert d.margin_l == 0
        assert d.margin_r == 0
        assert d.margin_v == 0
        assert d.effect == ""

    def test_kw_only(self):
        d = Dialog(text="Hi", layer=5, name="Actor")
        assert d.layer == 5
        assert d.name == "Actor"


class TestDialogFromAss:
    def test_basic(self):
        line = "Dialogue: 0,0:00:00.00,0:00:05.00,Default,,0,0,0,,Hello World"
        d = Dialog.from_ass(line)
        assert d.comment is False
        assert d.layer == 0
        assert d.start.time == 0
        assert d.end.time == 5000
        assert d.style == "Default"
        assert d.name == ""
        assert d.text == "Hello World"

    def test_comment(self):
        line = "Comment: 0,0:00:00.00,0:00:05.00,Default,,0,0,0,,Test comment"
        d = Dialog.from_ass(line)
        assert d.comment is True

    def test_all_fields(self):
        line = "Dialogue: 3,0:00:10.00,0:00:20.00,MyStyle,Actor,5,10,15,effect,Some text"
        d = Dialog.from_ass(line)
        assert d.layer == 3
        assert d.start.time == 10000
        assert d.end.time == 20000
        assert d.style == "MyStyle"
        assert d.name == "Actor"
        assert d.margin_l == 5
        assert d.margin_r == 10
        assert d.margin_v == 15
        assert d.effect == "effect"
        assert d.text == "Some text"

    def test_text_with_commas(self):
        line = "Dialogue: 0,0:00:00.00,0:00:05.00,Default,,0,0,0,,Hello, World"
        d = Dialog.from_ass(line)
        assert d.text == "Hello, World"

    def test_custom_format_order(self):
        fmt = (
            "Layer",
            "Start",
            "End",
            "Style",
            "Name",
            "MarginL",
            "MarginR",
            "MarginV",
            "Effect",
            "Text",
        )
        line = "Dialogue: 1,0:00:01.00,0:00:02.00,Alt,,0,0,0,,Test"
        d = Dialog.from_ass(line, fmt)
        assert d.layer == 1
        assert d.style == "Alt"

    def test_invalid_format_last_not_text(self):
        fmt = ("Layer", "Start", "End", "Style")
        with pytest.raises(ValueError):
            Dialog.from_ass("Dialogue: 0,0:00:00.00,0:00:05.00,Default", fmt)


class TestDialogToAss:
    def test_dialogue(self):
        d = Dialog(text="Hello")
        result = d.to_ass()
        assert result.startswith("Dialogue: ")

    def test_comment(self):
        d = Dialog(text="Comment text", comment=True)
        result = d.to_ass()
        assert result.startswith("Comment: ")

    def test_round_trip(self):
        original = "Dialogue: 0,0:00:01.00,0:00:02.50,Default,,0,0,0,,Test"
        d = Dialog.from_ass(original)
        result = d.to_ass()
        assert result.startswith("Dialogue: ")


class TestDialogAliases:
    def test_start_time(self):
        d = Dialog(text="")
        d.start_time = AssTime(5000)
        assert d.start.time == 5000
        assert d.start_time.time == 5000

    def test_end_time(self):
        d = Dialog(text="")
        d.end_time = AssTime(10000)
        assert d.end.time == 10000

    def test_actor(self):
        d = Dialog(text="")
        d.actor = "John"
        assert d.name == "John"
        assert d.actor == "John"


class TestDialogShift:
    def test_shift_forward(self):
        d = Dialog(text="", start=AssTime(1000), end=AssTime(2000))
        d.shift(500)
        assert d.start.time == 1500
        assert d.end.time == 2500

    def test_shift_backward(self):
        d = Dialog(text="", start=AssTime(1000), end=AssTime(2000))
        d.shift(-500)
        assert d.start.time == 500
        assert d.end.time == 1500


class TestDialogTextStripped:
    def test_no_tags(self):
        d = Dialog(text="Plain text")
        assert d.text_stripped == "Plain text"

    def test_with_tags(self):
        d = Dialog(text="{\\b1}Bold{\\b0} Normal")
        assert d.text_stripped == "Bold Normal"

    def test_escaped_braces(self):
        d = Dialog(text="\\{Not a tag\\}")
        assert d.text_stripped == "\\{Not a tag\\}"


class TestDialogParseTags:
    def test_parse_basic(self):
        d = Dialog(text="{\\b1}Bold{\\b0}")
        parsed = d.parse_tags()
        assert len(parsed) > 0

    def test_parse_plain_text(self):
        d = Dialog(text="Plain text")
        parsed = d.parse_tags()
        assert parsed.get_plain_text() == "Plain text"
