from __future__ import annotations

from typing import List

from utils.json_in_out import JsonInOut
from InputData.mvc.Model.point import Point


class LineSegment(JsonInOut):
    __slots__ = 'a', 'b'

    def __init__(self, a: Point, b: Point):
        self.a = a
        self.b = b

    def get_scale_copy(self, x: float = 1, y: float = 1) -> LineSegment:
        return LineSegment(Point(self.a.x * x, self.a.y * y), Point(self.b.x * x, self.b.y * y))

    def is_empty(self):
        return self.a.x is None or self.b.x is None

    def get_x(self) -> [float]:
        return [self.a.x, self.b.x]

    def get_y(self) -> [float]:
        return [self.a.y, self.b.y]

    def load_from_dict(self, load_dict: dict):
        for name_property in load_dict:
            if name_property == 'a':
                self.a = Point(load_dict=load_dict[name_property])
            elif name_property == 'b':
                self.b = Point(load_dict=load_dict[name_property])
            else:
                if hasattr(self, name_property):
                    self.__setattr__(name_property, load_dict[name_property])

    def get_scale_line(self, scale_x, scale_y) -> LineSegment:
        a = Point(round(self.a.x * scale_x), round(self.a.y * scale_y))
        b = Point(round(self.b.x * scale_x), round(self.b.y * scale_y))
        return LineSegment(a, b)


class PolygonalChain:
    __slots__ = 'dots'

    def __init__(self, x: [float], y: [float]):
        self.dots: List[Point] = []

        for x1, y1 in zip(x, y):
            self.add_dot(x1, y1)

    def is_empty(self) -> bool:
        return True if len(self.dots) < 1 else False

    def add_dot(self, x: float, y: float):
        self.dots.append(Point(x, y))

    def get_y(self) -> [float]:
        return [i.y for i in self.dots]

    def get_x(self) -> [float]:
        return [i.x for i in self.dots]

    def get_x_y(self) -> ([float], [float]):
        return self.get_x(), self.get_y()
