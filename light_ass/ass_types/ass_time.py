class AssTime:
    def __init__(self, time: "str | int | float | AssTime"):
        if isinstance(time, str):
            h, m, s = map(float, time.split(":"))
            self.time = int((h * 3600 + m * 60 + s) * 1000)
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
