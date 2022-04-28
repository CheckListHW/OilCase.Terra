from utils.json_in_out import JsonInOut


class AxisConstraints(JsonInOut):
    __slots__ = ['_start', '_end']

    def __init__(self, start, end):
        self._start = start
        self._end = end

    def change_constraints(self, start=None, end=None):
        self.start = start if start is not None else self.start
        self.end = end if end is not None else self.end

    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, value: int):
        self._start = abs(int(value))

    @property
    def end(self) -> int:
        return self._end

    @end.setter
    def end(self, value: int):
        self._end = abs(int(value))


class Size(JsonInOut):
    __slots__ = ['x_constraints', 'y_constraints', 'z_constraints']

    def __init__(self, x_start: int = 0, x_end: int = 25, y_start: int = 0, y_end: int = 25, z_start: int = 0,
                 z_end: int = 25, message=None):
        self.x_constraints = AxisConstraints(x_start, x_end)
        self.y_constraints = AxisConstraints(y_start, y_end)
        self.z_constraints = AxisConstraints(z_start, z_end)

    def change_constraints(self, x_start: int = None, x_end: int = None, y_start: int = None, y_end: int = None,
                           z_start: int = None, z_end: int = None):
        self.x_constraints.change_constraints(x_start, x_end)
        self.y_constraints.change_constraints(y_start, y_end)
        self.z_constraints.change_constraints(z_start, z_end)

    @property
    def x(self) -> int:
        return 25
        return int(abs(self.x_constraints.start - self.x_constraints.end))

    @property
    def y(self):
        return 25
        return int(abs(self.y_constraints.start - self.y_constraints.end))

    @property
    def z(self):
        return 500
        return int(abs(self.z_constraints.start - self.z_constraints.end))

    def max(self):
        return max([0, self.y, self.x, self.z])
