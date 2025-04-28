class AssTime:
    def __init__(self, time: "str | int | float | AssTime"):
        if isinstance(time, str):
            hours, minutes, seconds_ms = time.split(":")
            seconds, milliseconds = seconds_ms.split(".")
            self.time = (
                    int(hours) * 3600000 +
                    int(minutes) * 60000 +
                    int(seconds) * 1000 +
                    int(milliseconds.ljust(3, "0"))
            )
        elif isinstance(time, (int, float, AssTime)):
            self.time = int(time)
        else:
            raise TypeError("Unsupported type")

    def __repr__(self):
        return f"AssTime({self.time})"

    def __int__(self):
        return self.time

    def __str__(self):
        return self.to_string()

    def __eq__(self, other):
        return self.time == AssTime(other).time

    def __lt__(self, other):
        return self.time < AssTime(other).time

    def __gt__(self, other):
        return self.time > AssTime(other).time

    def __le__(self, other):
        return self.time <= AssTime(other).time

    def __ge__(self, other):
        return self.time >= AssTime(other).time

    def __add__(self, other):
        return AssTime(self.time + AssTime(other).time)

    def __radd__(self, other):
        return self + other

    def __iadd__(self, other):
        self.time += AssTime(other).time
        return self

    def __sub__(self, other):
        return AssTime(self.time - AssTime(other).time)

    def __rsub__(self, other):
        return AssTime(other) - self

    def __isub__(self, other):
        self.time -= AssTime(other).time
        return self

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return self.time / other
        return NotImplemented

    def __floordiv__(self, other):
        if isinstance(other, (int, float)):
            return AssTime(self.time // other)
        return NotImplemented

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return AssTime(int(self.time * other))
        return NotImplemented

    def __rmul__(self, other):
        return self * other

    def to_string(self) -> str:
        """
        Convert the time to a string.
        :return: The time as a string.
        """
        ms = max(0, int(round(self.time)))
        h, ms = divmod(ms, 3600000)
        m, ms = divmod(ms, 60000)
        s, ms = divmod(ms, 1000)
        return f"{h:01d}:{m:02d}:{s:02d}.{ms:03d}"[:-1]
