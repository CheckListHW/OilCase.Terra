from __future__ import annotations

from InputData.mvc.Model.line_segment import LineSegment
from InputData.mvc.Model.point import Point
from utils.json_in_out import JsonInOut


class Split(JsonInOut):
    __slots__ = 'depth', 'angle', '_line', 'from_start', 'a_offset_z', 'b_offset_z'

    def __init__(self, load_dict=None):
        self.depth: float = 0  # from .0 to 1.0
        self.angle: int = 0  # from
        self._line: LineSegment = LineSegment(Point(), Point())
        self.a_offset_z = 0
        self.b_offset_z = 0
        self.from_start = True

        if load_dict:
            self.load_from_dict(load_dict)

    @property
    def line(self) -> LineSegment:
        if self._line.a.y is not None and self._line.b.y is not None:
            if self._line.a.y > self._line.b.y:
                self._line.a, self._line.b = self._line.b, self._line.a
            if self._line.a.x > self._line.b.x:
                self._line.a, self._line.b = self._line.b, self._line.a
        return self._line

    @line.setter
    def line(self, value: LineSegment):
        self._line = value

    def load_from_dict(self, load_dict: dict):
        super(Split, self).load_from_dict(load_dict)
        if load_dict.get('_line') is not None:
            self._line = LineSegment(Point(), Point())
            self.line.load_from_dict(load_dict['_line'])

    def scale_split(self, scale) -> Split:
        scale_split = Split(load_dict=self.get_as_dict())
        scale_split.line = self.line.get_scale_line(scale, scale)
        return scale_split
