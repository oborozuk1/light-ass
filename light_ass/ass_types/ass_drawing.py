from typing import Self


class AssDrawing:
    def __init__(self, drawing: str | Self):
        if isinstance(drawing, str):
            self.drawing = drawing
        elif isinstance(drawing, AssDrawing):
            self.drawing = drawing.drawing
        else:
            raise ValueError("Unsupported type")

    def __eq__(self, other: str | Self):
        try:
            other = AssDrawing(other)
            return self.drawing == other.drawing
        except ValueError:
            return False

    def __str__(self):
        return self.drawing

    def __repr__(self):
        return f"AssDrawing({self.drawing})"