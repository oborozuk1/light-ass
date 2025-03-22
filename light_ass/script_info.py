from typing import Any, Self, Literal, overload

ScriptInfoKeys = Literal[
    "Title",
    "Original Script",
    "Original Translation",
    "Original Editing",
    "Original Timing",
    "Synch Point",
    "Script Updated By",
    "ScriptType",
    "Update Details",
    "PlayResX",
    "PlayResY",
    "PlayDepth",
    "ScaledBorderAndShadow",
    "WrapStyle",
    "YCbCr Matrix",
    "Collisions",
    "Timer",
    "LayoutResX",
    "LayoutResY",
    # libass extensions
    "Kerning",
    "Language",
]


class ScriptInfo(dict):
    _TYPE_RULES = {
        "PlayResX": int,
        "PlayResY": int,
        "LayoutResX": int,
        "LayoutResY": int,
        "PlayDepth": int,
        "WrapStyle": int,
        "ScaledBorderAndShadow": lambda s: s.lower() == "yes",
        "Kerning": lambda s: s.lower() == "yes",
    }

    def __init__(self, info: Self | dict[str, Any] | None = None):
        super().__init__()
        if isinstance(info, dict):
            for key, value in info.items():
                self[key] = value

    def __getitem__(self, key: ScriptInfoKeys | str):
        return super().__getitem__(key)

    def __setitem__(self, key: ScriptInfoKeys | str, value: Any) -> None:
        super().__setitem__(key, value)

    def set(self, key: ScriptInfoKeys | str, value):
        if value is None:
            self.pop(key)
        elif key in self._TYPE_RULES:
            try:
                super().__setitem__(key, self._TYPE_RULES[key](value))
            except ValueError:
                super().__setitem__(key, value)
        else:
            super().__setitem__(key, value)

    def __repr__(self) -> str:
        return f"ScriptInfo({super().__repr__()})"

    def __str__(self) -> str:
        infos = []
        for key, value in self.items():
            if isinstance(value, bool):
                value = "yes" if value else "no"
            infos.append(f"{key}: {value}")
        return "\n".join(infos)
