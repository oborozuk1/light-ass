from typing import Self


class AssTime:
    def __init__(self, time: str | int | Self):
        if isinstance(time, str):
            h, m, s = map(float, time.split(':'))
            self.time = int((h * 3600 + m * 60 + s) * 1000)
        elif isinstance(time, int):
            self.time = time
        elif isinstance(time, AssTime):
            self.time = time.time
        else:
            raise TypeError("Unsupported type")

    def __repr__(self):
        return f"AssTime({self.time})"

    def __int__(self) :
        return self.time

    def __str__(self):
        return self.to_str()

    def __eq__(self, other: str | int | Self):
        try:
            other = AssTime(other)
            return self.time == other.time
        except ValueError:
            return False

    def __lt__(self, other: str | int | Self):
        try:
            other = AssTime(other)
            return self.time < other.time
        except ValueError:
            raise TypeError("Unsupported type")

    def __gt__(self, other: str | int | Self):
        try:
            other = AssTime(other)
            return self.time > other.time
        except ValueError:
            raise TypeError("Unsupported type")

    def __add__(self, other: int | Self):
        if isinstance(other, int):
            return AssTime(self.time + other)
        elif isinstance(other, AssTime):
            return AssTime(self.time + other.time)
        raise TypeError("Unsupported type")

    def __radd__(self, other: int | Self):
        return self.__add__(other)

    def __sub__(self, other: int | Self):
        if isinstance(other, int):
            return AssTime(self.time - other)
        elif isinstance(other, AssTime):
            return AssTime(self.time - other.time)
        raise TypeError("Unsupported type")

    def __rsub__(self, other: int | Self):
        if isinstance(other, int):
            return AssTime(other - self.time)
        elif isinstance(other, AssTime):
            return AssTime(other.time - self.time)
        raise TypeError("Unsupported type")

    def to_str(self) -> str:
        """
        Convert the time to a string.
        :return: The time as a string.
        """
        ms = max(0, self.time)
        ms = int(round(ms))
        h, ms = divmod(ms, 3600000)
        m, ms = divmod(ms, 60000)
        s, ms = divmod(ms, 1000)
        return f"{h:01d}:{m:02d}:{s:02d}.{ms:03d}"[:-1]
