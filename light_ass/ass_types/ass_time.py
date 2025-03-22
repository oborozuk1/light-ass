from typing import Self


class AssTime(int):
    def __new__(cls, time: str | int | Self):
        if isinstance(time, int):
            return super().__new__(cls, time)
        if isinstance(time, str):
            h, m, s = map(float, time.split(':'))
            time = int((h * 3600 + m * 60 + s) * 1000)
            return super().__new__(cls, time)
        raise TypeError("Unsupported type")

    def __repr__(self):
        return f"AssTime({self})"

    def __str__(self):
        return self.to_str()

    def to_str(self) -> str:
        """
        Convert the time to a string.
        :return: The time as a string.
        """
        ms = max(0, self)
        ms = int(round(ms))
        h, ms = divmod(ms, 3600000)
        m, ms = divmod(ms, 60000)
        s, ms = divmod(ms, 1000)
        return f"{h:01d}:{m:02d}:{s:02d}.{ms:03d}"[:-1]
