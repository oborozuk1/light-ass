from typing import Any, Self, Literal

from .utils import validate_value

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
    _formats = {
        "Title": str,
        "Original Script": str,
        "Original Translation": str,
        "Original Editing": str,
        "Original Timing": str,
        "Synch Point": str,
        "Script Updated By": str,
        "ScriptType": str,
        "Update Details": str,
        "PlayResX": int,
        "PlayResY": int,
        "PlayDepth": int,
        "ScaledBorderAndShadow": {"yes": True, "no": False},
        "WrapStyle": (0, 1, 2, 3),
        "YCbCr Matrix": ("None", "TV.601", "PC.601", "TV.709", "PC.709", "TV.FCC", "PC.FCC", "TV.240M", "PC.240M"),
        "Collisions": ("Normal", "Reverse"),
        "Timer": float,
        "LayoutResX": int,
        "LayoutResY": int,
        # libass extensions
        "Kerning": {"yes": True, "no": False},
        "Language": str,
    }

    def __init__(self, info: Self | dict[str, Any] | None = None):
        super().__init__()
        if isinstance(info, dict):
            for key, value in info.items():
                self[key] = value

    def sort(self) -> None:
        """
        Sort the script info in default order.
        :return: None
        """
        mapping = {key: i for i, key in enumerate(self._formats.keys())}
        new = sorted(self.items(), key=lambda x: mapping.get(x[0], 99))
        self.clear()
        self.update(new)

    def __getitem__(self, key: ScriptInfoKeys | str):
        return super().__getitem__(key)

    def __setitem__(self, key: ScriptInfoKeys | str, value):
        if value is None:
            self.pop(key)
        else:
            super().__setitem__(key, self.validate_value(key, value))

    def __repr__(self) -> str:
        return f"ScriptInfo({super().__repr__()})"

    def __str__(self) -> str:
        infos = []
        for key, value in self.items():
            if isinstance(self._formats[key], dict):
                rev_dict = {v: k for k, v in self._formats[key].items()}
                value = rev_dict[value]
            infos.append(f"{key}: {value}")
        return "\n".join(infos)

    @staticmethod
    def validate_value(key, value):
        if key not in ScriptInfo._formats:
            return value
        try:
            return validate_value(ScriptInfo._formats[key], value)
        except ValueError:
            raise ValueError(f"Invalid value for {key}: {value}")
