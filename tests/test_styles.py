import pytest

from light_ass import Style, Styles


class TestStylesInit:
    def test_empty(self):
        s = Styles()
        assert len(s) == 0
        assert not s

    def test_from_list(self):
        s1 = Style(name="Default")
        s2 = Style(name="Alt")
        styles = Styles([s1, s2])
        assert len(styles) == 2
        assert "Default" in styles
        assert "Alt" in styles


class TestStylesDictInterface:
    def test_getitem(self):
        styles = Styles([Style(name="Default")])
        assert styles["Default"].name == "Default"

    def test_getitem_missing(self):
        styles = Styles()
        with pytest.raises(KeyError):
            styles["Nonexistent"]

    def test_setitem(self):
        styles = Styles()
        styles["Default"] = Style(name="Default")
        assert "Default" in styles
        assert styles["Default"].name == "Default"

    def test_setitem_renames(self):
        styles = Styles()
        styles["NewName"] = Style(name="OldName")
        assert styles["NewName"].name == "NewName"

    def test_delitem(self):
        styles = Styles([Style(name="Default")])
        del styles["Default"]
        assert len(styles) == 0

    def test_contains(self):
        styles = Styles([Style(name="Default")])
        assert "Default" in styles
        assert "Other" not in styles

    def test_iter(self):
        styles = Styles([Style(name="A"), Style(name="B")])
        assert set(styles) == {"A", "B"}

    def test_bool(self):
        assert not Styles()
        assert Styles([Style(name="A")])

    def test_get_with_default(self):
        styles = Styles()
        assert styles.get("X") is None
        default = Style(name="default")
        assert styles.get("X", default) is default

    def test_keys(self):
        styles = Styles([Style(name="A"), Style(name="B")])
        assert set(styles.keys()) == {"A", "B"}

    def test_values(self):
        s1 = Style(name="A")
        s2 = Style(name="B")
        styles = Styles([s1, s2])
        names = {s.name for s in styles.values()}
        assert names == {"A", "B"}

    def test_items(self):
        s1 = Style(name="A")
        styles = Styles([s1])
        assert list(styles.items()) == [("A", s1)]


class TestStylesSet:
    def test_set_new(self):
        styles = Styles()
        styles.set(Style(name="Default"))
        assert "Default" in styles

    def test_set_overwrite(self):
        s1 = Style(name="Default")
        styles = Styles([s1])
        s2 = Style(name="Default", bold=True)
        styles.set(s2)
        assert styles["Default"].bold is True


class TestStylesRename:
    def test_rename(self):
        styles = Styles([Style(name="Old")])
        styles.rename("Old", "New")
        assert "Old" not in styles
        assert "New" in styles
        assert styles["New"].name == "New"

    def test_rename_missing(self):
        styles = Styles()
        with pytest.raises(KeyError):
            styles.rename("Nonexistent", "New")

    def test_rename_conflict(self):
        styles = Styles([Style(name="A"), Style(name="B")])
        with pytest.raises(KeyError):
            styles.rename("A", "B")


class TestStylesFromAss:
    def test_basic(self):
        text = "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Default,Arial,48,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1"
        styles = Styles.from_ass(text)
        assert len(styles) == 1
        assert styles["Default"].fontname == "Arial"

    def test_multiple_styles(self):
        text = (
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
            "Style: A,Arial,48,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1\n"
            "Style: B,Arial,72,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1"
        )
        styles = Styles.from_ass(text)
        assert len(styles) == 2
        assert styles["A"].fontsize == 48.0
        assert styles["B"].fontsize == 72.0

    def test_no_format(self):
        text = "Style: Default,Arial,48,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1"
        styles = Styles.from_ass(text)
        assert len(styles) == 1

    def test_strict_missing_format(self):
        text = "Style: Default,Arial,48,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1"
        with pytest.raises(ValueError):
            Styles.from_ass(text, strict=True)


class TestStylesToAss:
    def test_empty(self):
        styles = Styles()
        result = styles.to_ass()
        assert result.startswith("Format: ")

    def test_one_style(self):
        styles = Styles([Style(name="Default")])
        result = styles.to_ass()
        assert "Style: Default" in result

    def test_repr(self):
        styles = Styles([Style(name="A"), Style(name="B")])
        assert repr(styles) == "Styles(A, B)"
