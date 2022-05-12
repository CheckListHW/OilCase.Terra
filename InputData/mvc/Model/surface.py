from __future__ import annotations

from copy import deepcopy
from typing import Callable, Optional, List

from InputData.mvc.Model.line_segment import LineSegment
from InputData.mvc.Model.point import Point
from InputData.mvc.Model.size import Size
from utils.recursive_extraction_of_list import recursive_extraction
from res.strings import Limits


class SurfacePropertyMemento:
    __slots__ = ['target', 'history', 'current_version']

    def __init__(self, obj: SurfaceProperty):
        self.target = obj
        self.history: [SurfaceProperty] = list()
        self.add()
        self.current_version = -1

    def get_prev(self):
        self.current_version = self.current_version - 1 if self.current_version > 0 else 0
        try:
            surf = self.history[self.current_version]
        except IndexError:
            self.current_version = 0
            surf = self.history[self.current_version]

        self.target.set_from_copy(surf)

    def add(self):
        sum_size = 0
        for s in self.history:
            sum_size += s.__sizeof__()

        if len(self.history) > 100:
            self.history.pop(0)
        self.current_version = len(self.history) - 1
        self.history.append(self.target.get_copy())

    def get_next(self):
        self.current_version += 1
        try:
            surf = self.history[self.current_version]
        except IndexError:
            self.current_version = len(self.history) - 1
            surf = self.history[self.current_version]
        self.target.set_from_copy(surf)


def get_border_value(value: [Optional[float]], border: ()) -> Optional[float]:
    v = [i for i in value if i is not None]
    return border(v) if v else None


class SurfaceProperty:  # z - высота слоя
    __slots__ = 'pre_x', 'pre_y', 'start_x', 'start_y', 'x', 'y', '_z', \
                'primary', 'size', 'splits', 'current_split'

    def __init__(self, size: Size = None, z: int = -1):
        self.pre_x: Optional[float] = None
        self.pre_y: Optional[float] = None
        self.start_x: Optional[float] = None
        self.start_y: Optional[float] = None

        self.current_split: int = 0
        self.splits: List[LineSegment] = []  # split = [start, end]

        self.x: [float] = list()
        self.y: [float] = list()

        self._z = z
        self.size = size
        self.primary = True

    @property
    def z(self) -> int:
        return self._z

    @z.setter
    def z(self, value: int):
        if value in range(Limits.MIN_HEIGHT, Limits.MAX_HEIGHT + 1):
            self._z = value
        elif value > Limits.MAX_HEIGHT:
            self._z = Limits.MAX_HEIGHT

    @property
    def curve(self) -> ([float], [float]):
        if self.x and self.y:
            if self.x[0] != self.x[-1] or self.y[0] != self.y[-1]:
                return self.x + [self.x[0]], self.y + [self.y[0]]
        return self.x, self.y

    @curve.setter
    def curve(self, value: ([float], [float])):
        self.x, self.y = value

    @property
    def scalable_curve(self) -> ([float], [float]):
        x, y = self.curve
        if self.size:
            x = [i * (self.size.x / Limits.BASE_PLOT_SCALE) for i in x]
            y = [i * (self.size.y / Limits.BASE_PLOT_SCALE) for i in y]
        return x, y

    def get_min_x_and_y(self):
        x, y = self.scalable_curve
        return get_border_value(x, min), get_border_value(y, min)

    def get_max_x_and_y(self):
        x, y = self.scalable_curve
        return get_border_value(x, max), get_border_value(y, max)

    @property
    def scalable_split(self) -> [LineSegment]:
        scalale_splits: List[LineSegment] = []
        for split in self.splits:
            if split.a.x is not None and split.b.x is not None:
                p_a = Point(split.a.x * self.size.x, split.a.y * self.size.y)
                p_b = Point(split.b.x * self.size.x, split.b.y * self.size.y)
                scalale_splits.append(LineSegment(p_a, p_b))
        return scalale_splits

    def get_copy(self) -> SurfaceProperty:
        this_copy = SurfaceProperty()
        self.__copying(self, this_copy)
        return this_copy

    @staticmethod
    def __copying(from_property: SurfaceProperty, to_property: SurfaceProperty):
        for slot in SurfaceProperty.__slots__:
            attribute_name = slot.replace('__', '')
            if hasattr(from_property.__getattribute__(attribute_name), "copy"):
                copy_attribute = deepcopy(from_property.__getattribute__(attribute_name))
                to_property.__setattr__(attribute_name, copy_attribute)
            else:
                attribute = from_property.__getattribute__(attribute_name)
                to_property.__setattr__(attribute_name, attribute)

    def set_from_copy(self, copy: SurfaceProperty):
        self.__copying(copy, self)

    def get_as_dict(self) -> dict:
        my_dict = {}
        this_class = SurfaceProperty
        for slot in this_class.__slots__:
            my_dict[slot] = recursive_extraction(getattr(self, slot))
        return my_dict

    def load_from_dict(self, load_dict: dict):
        for name_property in load_dict:
            if name_property.__contains__('x'):
                self.x = load_dict[name_property]
            elif name_property == 'size':
                pass
            elif name_property == 'splits':
                self.splits = []
                for split in load_dict[name_property]:
                    self.splits.append(LineSegment(Point(), Point()))
                    self.splits[-1].load_from_dict(split)
            else:
                if hasattr(self, name_property):
                    self.__setattr__(name_property, load_dict[name_property])

    def add_dot(self, x1: float, y1: float):
        self.x.append(x1)
        self.y.append(y1)

    def change_dot_split(self, dot_x: float, dot_y: float, start_line: bool = True):
        while len(self.splits) <= self.current_split:
            self.splits.append(LineSegment(Point(), Point()))

        if start_line:
            self.splits[self.current_split].a.set(dot_x, dot_y)
        else:
            self.splits[self.current_split].b.set(dot_x, dot_y)
        if self.splits[self.current_split].a == self.splits[self.current_split].b:
            self.splits[self.current_split].a.set(None, None)
            self.splits[self.current_split].b.set(None, None)

    def clear(self):
        self.x, self.y = list(), list()


class Surface(SurfaceProperty):
    __slots__ = ['__prev_layer', '__next_layer', 'memento']

    def __init__(self, size: Size, z: int = -1, load_dict: dict = None):
        super(Surface, self).__init__(size, z)
        self.__next_layer: () = lambda x: None
        self.__prev_layer: () = lambda x: None
        self.memento = SurfacePropertyMemento(self)

        if load_dict:
            self.load_from_dict(load_dict)

    @property
    def prev_layer(self) -> Optional[Surface]:
        return self.__prev_layer(self.z)

    @prev_layer.setter
    def prev_layer(self, method: Callable):
        self.__prev_layer = method

    @property
    def next_layer(self) -> Optional[Surface]:
        return self.__next_layer(self.z)

    @next_layer.setter
    def next_layer(self, method):
        self.__next_layer = method

    def dot_value_change(self, index, x, y) -> None:
        if self.x and self.y:
            if 0 <= index <= len(self.x):
                self.x[index], self.y[index] = x, y
                self.memento.add()

    def insert_dot(self, index: int, x1: float, y1: float):
        if type(index) is int:
            self.x.insert(index, x1)
            self.y.insert(index, y1)
            self.memento.add()
        else:
            print('type error: index is ', type(index), ' = ', index)

    def pop_dot(self, index: int):
        if index in range(0, len(self.x) + 1):
            self.x.pop(index)
            self.y.pop(index)
            self.memento.add()

    def set_pre_dot(self, x1: float, y1: float):
        self.pre_x, self.pre_y = x1, y1
        self.add_dot(x1, y1)

    def set_start_dot(self, x1: float, y1: float):
        self.start_x, self.start_y = x1, y1
        self.set_pre_dot(x1, y1)

    def add_dot(self, x1: float, y1: float):
        self.insert_dot(len(self.x), x1, y1)

    def change_dot_split(self, dot_x: float, dot_y: float, start_line: bool = True):
        self.memento.add()
        self.primary = True
        super(Surface, self).change_dot_split(dot_x, dot_y, start_line)

    def clear(self):
        self.memento.add()
        super(Surface, self).clear()


def get_square_surface(size: Size, z: int, s: float = 24.99) -> Surface:
    surf = Surface(size)
    for i, j in [(0.1, 0.1), (0.1, s), (s, s), (s, 0.1), (0.1, 0.1)]:
        surf.add_dot(i, j)
    surf.z = z
    return surf
