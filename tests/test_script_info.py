import pytest

from light_ass import ScriptInfo


class TestScriptInfoInit:
    def test_empty(self):
        info = ScriptInfo()
        assert len(info) == 0
        assert not info

    def test_from_dict(self):
        info = ScriptInfo({"Title": "test", "PlayResX": 1920})
        assert info["Title"] == "test"
        assert info["PlayResX"] == 1920
        assert len(info) == 2

    def test_from_another_script_info(self):
        info1 = ScriptInfo({"Title": "test"})
        info2 = ScriptInfo(info1)
        assert info2["Title"] == "test"


class TestScriptInfoDictInterface:
    def test_get_set_del(self):
        info = ScriptInfo()
        info["Title"] = "My Title"
        assert info["Title"] == "My Title"
        assert len(info) == 1
        del info["Title"]
        assert len(info) == 0

    def test_not_found_raises_key_error(self):
        info = ScriptInfo()
        with pytest.raises(KeyError):
            info["Nonexistent"]

    def test_contains(self):
        info = ScriptInfo({"Title": "test"})
        assert "Title" in info
        assert "Other" not in info

    def test_iter(self):
        info = ScriptInfo({"A": 1, "B": 2})
        assert set(info) == {"A", "B"}

    def test_bool_false(self):
        assert not ScriptInfo()

    def test_bool_true(self):
        assert ScriptInfo({"A": 1})

    def test_get_with_default(self):
        info = ScriptInfo()
        assert info.get("X", "default") == "default"
        info["X"] = 42
        assert info.get("X") == 42

    def test_keys(self):
        info = ScriptInfo({"A": 1, "B": 2})
        assert set(info.keys()) == {"A", "B"}

    def test_values(self):
        info = ScriptInfo({"A": 1, "B": 2})
        assert set(info.values()) == {1, 2}

    def test_items(self):
        info = ScriptInfo({"A": 1})
        assert info.items() == [("A", 1)]


class TestScriptInfoSet:
    def test_set_with_type_parsing(self):
        info = ScriptInfo()
        info.set("PlayResX", "1920", parse=True)
        assert info["PlayResX"] == 1920

    def test_set_wrapstyle(self):
        info = ScriptInfo()
        info.set("WrapStyle", "3", parse=True)
        assert info["WrapStyle"] == 3

    def test_set_scaled_border(self):
        info = ScriptInfo()
        info.set("ScaledBorderAndShadow", "yes", parse=True)
        assert info["ScaledBorderAndShadow"] is True

    def test_set_kerning(self):
        info = ScriptInfo()
        info.set("Kerning", "yes", parse=True)
        assert info["Kerning"] is True

    def test_set_none_value_removes_key(self):
        info = ScriptInfo({"Title": "test"})
        info.set("Title", None)
        assert "Title" not in info

    def test_set_untyped_key(self):
        info = ScriptInfo()
        info.set("Custom", "value")
        assert info["Custom"] == "value"


class TestScriptInfoFromAss:
    def test_simple(self):
        text = "Title: My Title\nPlayResX: 1920\nPlayResY: 1080"
        info = ScriptInfo.from_ass(text)
        assert info["Title"] == "My Title"
        assert info["PlayResX"] == 1920
        assert info["PlayResY"] == 1080

    def test_with_comments(self):
        text = "; This is a comment\nTitle: Test"
        info = ScriptInfo.from_ass(text)
        assert info["Title"] == "Test"
        assert "This is a comment" in info.messages

    def test_with_bang_comments(self):
        text = "!: Warning message\nTitle: Test"
        info = ScriptInfo.from_ass(text)
        assert info["Title"] == "Test"
        assert "Warning message" in info.messages

    def test_strict_mode(self):
        info = ScriptInfo.from_ass("Title: Test", strict=True)
        assert info["Title"] == "Test"


class TestScriptInfoToAss:
    def test_string_value(self):
        info = ScriptInfo({"Title": "Test"})
        assert info.to_ass() == "Title: Test"

    def test_bool_true(self):
        info = ScriptInfo({"ScaledBorderAndShadow": True})
        assert info.to_ass() == "ScaledBorderAndShadow: yes"

    def test_bool_false(self):
        info = ScriptInfo({"ScaledBorderAndShadow": False})
        assert info.to_ass() == "ScaledBorderAndShadow: no"

    def test_int_value(self):
        info = ScriptInfo({"PlayResX": 1920})
        assert info.to_ass() == "PlayResX: 1920"

    def test_multiple_keys(self):
        info = ScriptInfo({"Title": "Test", "PlayResX": 1920})
        result = info.to_ass()
        assert "Title: Test" in result
        assert "PlayResX: 1920" in result


class TestScriptInfoUnion:
    def test_or(self):
        info = ScriptInfo({"A": 1})
        result = info | {"B": 2}
        assert result == {"A": 1, "B": 2}
        assert isinstance(result, dict)

    def test_ror(self):
        result = {"A": 1} | ScriptInfo({"B": 2})
        assert result == {"A": 1, "B": 2}

    def test_ior(self):
        info = ScriptInfo({"A": 1})
        info |= {"B": 2}
        assert info["A"] == 1
        assert info["B"] == 2


class TestScriptInfoRepr:
    def test_repr(self):
        info = ScriptInfo({"Title": "Test"})
        assert "Title" in repr(info)
