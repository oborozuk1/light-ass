from .curly import TagParser
from .document import Document
from .events import Dialog, Events
from .parsed_event import ParsedDialog
from .script_info import ScriptInfo
from .styles import Style, Styles
from .types import AssAlpha, AssColor, AssShape, AssTime

__version__ = "0.2.1"

load = Document.load
from_string = Document.from_string

__all__ = [
    "AssAlpha",
    "AssColor",
    "AssShape",
    "AssTime",
    "Dialog",
    "Document",
    "Events",
    "ScriptInfo",
    "Style",
    "Styles",
    "ParsedDialog",
    "TagParser",
    "__version__",
    "load",
    "from_string",
]
