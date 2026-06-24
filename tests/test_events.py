import pytest

from light_ass import AssTime, Dialog, Events


class TestEventsInit:
    def test_empty(self):
        e = Events()
        assert len(e) == 0
        assert not e

    def test_from_list(self):
        d1 = Dialog(text="A")
        d2 = Dialog(text="B")
        e = Events([d1, d2])
        assert len(e) == 2
        assert e[0] is d1
        assert e[1] is d2


class TestEventsListInterface:
    def test_getitem(self):
        d = Dialog(text="Test")
        e = Events([d])
        assert e[0] is d

    def test_setitem(self):
        d1 = Dialog(text="A")
        d2 = Dialog(text="B")
        e = Events([d1])
        e[0] = d2
        assert e[0] is d2

    def test_setitem_slice(self):
        d1 = Dialog(text="A")
        d2 = Dialog(text="B")
        e = Events([])
        e[0:0] = [d1, d2]
        assert len(e) == 2

    def test_len(self):
        e = Events([Dialog(text="A"), Dialog(text="B")])
        assert len(e) == 2

    def test_iter(self):
        d1 = Dialog(text="A")
        d2 = Dialog(text="B")
        e = Events([d1, d2])
        assert list(e) == [d1, d2]

    def test_bool(self):
        assert not Events()
        assert Events([Dialog(text="A")])

    def test_index_error(self):
        e = Events()
        with pytest.raises(IndexError):
            e[0]


class TestEventsAppend:
    def test_append(self):
        e = Events()
        e.append(Dialog(text="Hello"))
        assert len(e) == 1

    def test_extend(self):
        e = Events()
        e.extend([Dialog(text="A"), Dialog(text="B")])
        assert len(e) == 2


class TestEventsPop:
    def test_pop_last(self):
        d = Dialog(text="Test")
        e = Events([d])
        popped = e.pop()
        assert popped is d
        assert len(e) == 0

    def test_pop_index(self):
        e = Events([Dialog(text="A"), Dialog(text="B")])
        popped = e.pop(0)
        assert popped.text == "A"
        assert len(e) == 1

    def test_pop_multiple(self):
        e = Events([Dialog(text="A"), Dialog(text="B"), Dialog(text="C")])
        popped = e.pop([0, 2])
        assert len(popped) == 2
        assert popped[0].text == "A"
        assert popped[1].text == "C"
        assert len(e) == 1
        assert e[0].text == "B"

    def test_pop_default(self):
        e = Events([Dialog(text="A"), Dialog(text="B")])
        popped = e.pop()
        assert popped.text == "B"


class TestEventsSort:
    def test_sort_default_by_start(self):
        d1 = Dialog(text="B", start=AssTime(2000))
        d2 = Dialog(text="A", start=AssTime(1000))
        d3 = Dialog(text="C", start=AssTime(3000))
        e = Events([d1, d2, d3])
        e.sort()
        assert e[0].text == "A"
        assert e[1].text == "B"
        assert e[2].text == "C"

    def test_sort_custom_key(self):
        d1 = Dialog(text="A", layer=3)
        d2 = Dialog(text="B", layer=1)
        d3 = Dialog(text="C", layer=2)
        e = Events([d1, d2, d3])
        e.sort(key=lambda x: x.layer)
        assert e[0].text == "B"
        assert e[1].text == "C"
        assert e[2].text == "A"


class TestEventsShift:
    def test_shift_all(self):
        d1 = Dialog(text="A", start=AssTime(1000), end=AssTime(2000))
        d2 = Dialog(text="B", start=AssTime(3000), end=AssTime(4000))
        e = Events([d1, d2])
        e.shift(500)
        assert e[0].start.time == 1500
        assert e[0].end.time == 2500
        assert e[1].start.time == 3500
        assert e[1].end.time == 4500

    def test_shift_range(self):
        d1 = Dialog(text="A", start=AssTime(1000), end=AssTime(2000))
        d2 = Dialog(text="B", start=AssTime(3000), end=AssTime(4000))
        e = Events([d1, d2])
        e.shift(500, range_=[0])
        assert e[0].start.time == 1500
        assert e[1].start.time == 3000


class TestEventsFromAss:
    def test_basic(self):
        text = (
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
            "Dialogue: 0,0:00:00.00,0:00:05.00,Default,,0,0,0,,Hello\n"
            "Dialogue: 0,0:00:05.00,0:00:10.00,Default,,0,0,0,,World"
        )
        e = Events.from_ass(text)
        assert len(e) == 2
        assert e[0].text == "Hello"
        assert e[1].text == "World"

    def test_no_format(self):
        text = "Dialogue: 0,0:00:00.00,0:00:05.00,Default,,0,0,0,,Hello"
        e = Events.from_ass(text)
        assert len(e) == 1

    def test_strict_missing_format(self):
        text = "Dialogue: 0,0:00:00.00,0:00:05.00,Default,,0,0,0,,Hello"
        with pytest.raises(ValueError):
            Events.from_ass(text, strict=True)

    def test_strict_duplicate_format(self):
        text = (
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
            "Dialogue: 0,0:00:00.00,0:00:05.00,Default,,0,0,0,,Hello"
        )
        with pytest.raises(ValueError):
            Events.from_ass(text, strict=True)


class TestEventsToAss:
    def test_empty(self):
        e = Events()
        result = e.to_ass()
        assert result.startswith("Format: ")

    def test_one_event(self):
        e = Events([Dialog(text="Hello")])
        result = e.to_ass()
        assert "Dialogue: " in result

    def test_repr(self):
        e = Events([Dialog(text="A"), Dialog(text="B")])
        assert "2 dialogs" in repr(e)
