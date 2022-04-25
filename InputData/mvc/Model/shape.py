from __future__ import annotations

import random
from typing import List, Optional

from InputData.data_resource.digit_value import Limits
from InputData.mvc.Model.line_segment import LineSegment
from InputData.mvc.Model.point import Point
from InputData.mvc.Model.size import Size
from InputData.mvc.Model.split import Split
from InputData.mvc.Model.surface import Surface, get_square_surface
from utils.filedialog import dict_from_json
from utils.geometry.angle_line import intersection_segment_dot
from utils.geometry.calc_offset import calc_offset
from utils.geometry.intersection_point_horizontal_plane import intersection_point_horizontal_plane
from utils.geometry.point_in_polygon import check_point_in_polygon
from utils.geometry.simplify_line import simplify_line
from utils.geometry.split_square import rectangle, split_square
from utils.observer import Subject
from utils.recursive_extraction_of_list import recursive_extraction


def split_shape_with_start_param(cur_shape: Shape, x_off, y_off) -> (Shape, Shape):
    cur_shape.split_parts = a_shape, b_shape = [Shape(cur_shape.size), Shape(cur_shape.size)]
    a_shape.sub_name = cur_shape.sub_name + '_a'
    b_shape.sub_name = cur_shape.sub_name + '_b'

    a_shape.x_offset = cur_shape.x_offset + x_off
    a_shape.y_offset = cur_shape.y_offset + y_off
    b_shape.x_offset = cur_shape.x_offset + x_off
    b_shape.y_offset = cur_shape.y_offset + y_off

    r, g, b = cur_shape.color
    ceil: () = lambda i, m: sorted([0, i, m])[1]
    similar_color = lambda val: ceil(int((val + 0.5 * val * (random.random() - 0.5))), 255)

    a_shape.color = (similar_color(i) for i in [r, g, b])
    b_shape.color = (similar_color(i) for i in [r, g, b])

    a_shape.layers.pop()
    b_shape.layers.pop()
    return a_shape, b_shape


# alpha - прозрачность от 0 до 1
class ShapeProperty(Subject):
    __slots__ = 'size', 'visible', '_alpha', 'sub_name', '_priority', '_color', 'name', 'x_offset', 'y_offset', \
                'layers', 'split_shapes', 'parts_property', 'presence_intermediate_layers', \
                '_filler', '_offset'

    def __init__(self, size: Size):
        super(ShapeProperty, self).__init__()
        self._filler = False
        self._offset, self.x_offset, self.y_offset = 0, 0, 0
        self.visible, self._alpha, self._priority = True, 0.9, 100
        self.presence_intermediate_layers = False
        self.name: str = 'layer 1'
        self.sub_name = ''
        self._color: (int, int, int) = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.size = size

        self.parts_property = {}  # name: ShapeProperty
        self.split_shapes: [Shape] = []

        self.layers: List[Surface] = list()

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, value):
        self._offset = value

    @property
    def filler(self):
        return self._filler

    @filler.setter
    def filler(self, value: bool):
        self._filler = value
        if self._filler:
            self.priority = 1
            self.alpha = 0.1

    @property
    def alpha(self):
        return self._alpha

    @alpha.setter
    def alpha(self, value: float):
        if 0 <= value <= 1:
            self._alpha = value

    @property
    def color(self) -> (int, int, int):
        return self._color

    @color.setter
    def color(self, value: (int, int, int)):
        r, g, b = value
        if int(r) in range(256) and int(g) in range(256) and int(b) in range(256):
            self._color = [r, g, b]

    @property
    def height(self) -> int:
        if self.layers:
            return max(self.layers, key=lambda i: i.z).z
        else:
            return 0

    @property
    def height_with_offset(self) -> int:
        layers = self.layers.copy()
        for shape in self.split_shapes:
            for l in shape.layers:
                layers.append(l)
        return max(layers, key=lambda i: i.z).z

    @property
    def priority(self) -> int:
        return self._priority

    @priority.setter
    def priority(self, value: int):
        value = int(value)
        if value in range(101):
            self._priority = value

    def get_as_dict(self) -> dict:
        my_dict = {}
        this_class = ShapeProperty
        for slot in this_class.__slots__:
            my_dict[slot] = recursive_extraction(getattr(self, slot))
        return my_dict

    def load_from_dict(self, data_dict: dict):
        for name_property in data_dict:
            if name_property == 'layers':
                self.layers = [Surface(size=self.size, load_dict=lay_dict) for lay_dict in data_dict[name_property]]
            elif name_property == 'parts_property':
                self.parts_property = {}
                for part_name in data_dict[name_property]:
                    load_dict = data_dict[name_property][part_name]
                    self.parts_property[part_name] = Shape(size=self.size, load_dict=load_dict)
            else:
                if hasattr(self, name_property):
                    if hasattr(self.__getattribute__(name_property), 'load_from_dict'):
                        self.__getattribute__(name_property).load_from_dict(data_dict[name_property])
                    else:
                        self.__setattr__(name_property, data_dict[name_property])
        self.notify()


class Shape(ShapeProperty):
    def __init__(self, size: Size, path: str = None, load_dict=None) -> None:
        super().__init__(size)
        self.add_layer(Surface(size=self.size, z=0))

        if path:
            self.load_from_json(path)
        if load_dict:
            self.load_from_dict(load_dict)

    def __add_offset_x_y(self, shape: Shape):
        p_prop, a_name = self.parts_property, shape.sub_name
        a_offset = p_prop.get(a_name).offset if p_prop.get(a_name) is not None else 0
        if len(shape.layers):
            lay = shape.layers[-1]

            lay.x = [x + a_offset * shape.x_offset for x in lay.x]
            lay.y = [y + a_offset * shape.y_offset for y in lay.y]

    def __prepare_layer_for_split(self, lay_main, a_shape: Shape, b_shape: Shape) -> (Surface, Surface):
        a_shape.layers.append(lay_main.get_copy())
        b_shape.layers.append(lay_main.get_copy())
        a_shape.layers[-1].size = b_shape.layers[-1].size = self.size
        lay_a, lay_b = a_shape.layers[-1], b_shape.layers[-1]
        lay_a.clear()
        lay_b.clear()

        return lay_a, lay_b

    def __shapes_set_offsets(self, shapes: [Shape]):
        for shape in shapes:
            self.__add_offset_x_y(shape)
            self.add_part_property(shape)
            if shape.offset > 0:
                for surf in shape.layers:
                    surf.z += shape.offset

    def __split_polygon(self, split: Split, lay_main: Surface, x_off: float, y_off: float) -> (
            ([float], [float]), ([float], [float]), Point, Point):
        a_x, a_y, b_x, b_y = split.line.a.x, split.line.a.y, split.line.b.x, split.line.b.y

        level = lay_main.z if split.from_start else max(self.layers, key=lambda i: i.z).z - lay_main.z
        level -= sorted(self.layers, key=lambda i: i.z)[0].z

        a_x, a_y = a_x + (x_off * level), a_y + (y_off * level)
        b_x, b_y = b_x + (x_off * level), b_y + (y_off * level)
        old_split_level = LineSegment(Point(a_x, a_y), Point(b_x, b_y))

        scale = Limits.BASEPLOTSCALE
        a_polygon, b_polygon, split_level = split_square(rectangle(scale, scale), old_split_level)

        x1, x2, y1, y2 = old_split_level.a.x, old_split_level.b.x, old_split_level.a.y, old_split_level.b.y
        a_sum = sum([(a.x - x1) * (y2 - y1) - (a.y - y1) * (x2 - x1) for a in a_polygon.dots])
        b_sum = sum([(b.x - x1) * (y2 - y1) - (b.y - y1) * (x2 - x1) for b in b_polygon.dots])
        if a_sum < 0 or b_sum > 0:
            a_polygon, b_polygon = b_polygon, a_polygon

        return a_polygon.get_x_y(), b_polygon.get_x_y(), split_level.a, split_level.b

    def add_layer(self, layer: Surface = None) -> Surface:
        return self.insert_layer(len(self.layers), layer)

    def add_part_property(self, shape: Shape):
        if shape == self:
            return

        if self.parts_property.get(shape.sub_name) is None:
            self.parts_property[shape.sub_name] = shape
        else:
            shape.name = self.parts_property[shape.sub_name].name = self.name
            shape.visible = self.parts_property.get(shape.sub_name).visible
            shape.offset = int(round(self.parts_property.get(shape.sub_name).offset))
            # shape.color = self.parts_property.get(shape.sub_name).color
            shape.alpha = self.alpha
            shape.priority = self.priority

    def calc_intermediate_layers(self):
        self.delete_secondary_surface()
        this_layers = [lay for lay in self.layers if len(lay.curve[0]) > 0]

        if not this_layers:
            return

        dot_count = len(min(this_layers, key=lambda layer: len(layer.x)).x)
        new_layers = [this_layers[0]]

        for i in range(len(this_layers) - 1):
            top_z = this_layers[i].z
            bottom_z = this_layers[i + 1].z

            top_lay_x, top_lay_y = this_layers[i].curve
            top_lay_x, top_lay_y = simplify_line(top_lay_x, top_lay_y, dot_count)

            bottom_lay_x, bottom_lay_y = this_layers[i + 1].curve
            bottom_lay_x, bottom_lay_y = simplify_line(bottom_lay_x, bottom_lay_y, dot_count)

            for loc_z in range(top_z + 1, bottom_z):
                intermediate_lay = Surface(z=loc_z, size=self.size)
                intermediate_lay.primary = False

                for dot_n in range(dot_count):
                    a = [top_lay_x[dot_n], top_lay_y[dot_n], top_z]
                    b = [bottom_lay_x[dot_n], bottom_lay_y[dot_n], bottom_z]
                    x, y, _ = intersection_point_horizontal_plane(a, b, loc_z)
                    intermediate_lay.add_dot(x, y)

                new_layers.append(intermediate_lay)

            new_layers.append(this_layers[i + 1])

        self.presence_intermediate_layers = True
        self.layers = new_layers

    def delete_secondary_surface(self):
        self.presence_intermediate_layers = False
        self.layers = [lay for lay in self.layers if lay.primary is True]

    def get_next_layer(self, z: int) -> Optional[Surface]:
        layers_less = [lay for lay in self.layers if lay.z < z]
        if layers_less:
            return sorted(layers_less, key=lambda i: i.z)[-1]

    def get_prev_layer(self, z: int) -> Optional[Surface]:
        layers_bigger = [lay for lay in self.layers if lay.z > z]
        if layers_bigger:
            return sorted(layers_bigger, key=lambda i: i.z)[0]

    def insert_layer(self, index: int, layer: Surface = None) -> Optional[Surface]:
        if not layer:
            layer = Surface(size=self.size)

        if index <= 0:
            if [lay for lay in self.layers if lay.z <= 0]:
                return None
            layer.z = self.layers[0].z - 1 if self.layers else 0
            self.layers.insert(0, layer)

        elif 0 < index < len(self.layers):
            if abs(self.layers[index - 1].z - self.layers[index].z) < 2:
                return None
            layer.z = int((self.layers[index - 1].z + self.layers[index].z) / 2)
            self.layers.insert(index, layer)

        elif index >= len(self.layers):
            if [lay for lay in self.layers if lay.z >= Limits.MAXHEIGHT]:
                return None
            layer.z = layer.z if layer.z > 0 else self.layers[-1].z + 1 if self.layers else 0
            self.layers.append(layer)

        layer.prev_layer = self.get_prev_layer
        layer.next_layer = self.get_next_layer
        return layer

    def load_from_dict(self, data_dict: dict):
        super(Shape, self).load_from_dict(data_dict)
        if self.presence_intermediate_layers:
            self.calc_intermediate_layers()

    def load_from_json(self, path: str):
        self.load_from_dict(dict_from_json(path))

    def pop_layer(self, index: int):
        if len(self.layers) < 2:
            return
        index = index if index in range(0, self.height + 1) else 0 if index <= 0 else len(self.layers) - 1
        self.layers.pop(index)
        # self.notify()

    def set_filler(self, value: bool):
        self.filler = value
        if self.filler:
            self.layers = []
            self.parts_property = {}
            self.add_layer(get_square_surface(self.size, 0, 24.99))

            surf = Surface(self.size, load_dict=self.layers[-1].get_as_dict())

            self.add_layer(surf)
            surf.z = self.size.z

    def set_layer_z(self, index, value):
        self.layers[index].z = value

    def sorted_layers(self):
        self.layers = sorted(self.layers, key=lambda lay: lay.z)
        return self.layers

    def splitting_shape(self, splits: [Split]) -> [Shape]:
        if self.filler:
            return [self]

        local_splits = [split.scale_split(Limits.BASEPLOTSCALE) for split in
                        [split for split in splits if not split.line.is_empty()]]

        self.split_shapes = [self]

        for split in local_splits:
            x_offset, y_offset = calc_offset(split.angle, split.line)
            copy_split_shapes = self.split_shapes.copy()
            self.split_shapes = []
            for cur_shape in copy_split_shapes:
                a_shape, b_shape = split_shape_with_start_param(cur_shape, x_offset, y_offset)
                for lay_main in [lay_main for lay_main in cur_shape.layers if len(lay_main.curve[0]) > 1]:
                    lay_x, lay_y = lay_main.curve

                    ((a_poly_x, a_poly_y), (b_poly_x, b_poly_y), a_split, b_split) = \
                        self.__split_polygon(split, lay_main, x_offset, y_offset)
                    lay_a, lay_b = self.__prepare_layer_for_split(lay_main, a_shape, b_shape)

                    d = [lay_x[0], lay_y[0]]

                    for i, j in zip(lay_x, lay_y):
                        c, d = d, [i, j]
                        if a_split.x is not None:

                            x1, y1 = intersection_segment_dot(a_split, b_split, Point(c[0], c[1]), Point(d[0], d[1]))
                            if x1 is not None and y1 is not None:
                                lay_a.add_dot(x1, y1)
                                lay_b.add_dot(x1, y1)

                        if check_point_in_polygon(a_poly_x, a_poly_y, i, j):
                            lay_a.add_dot(i, j)
                        if check_point_in_polygon(b_poly_x, b_poly_y, i, j):
                            lay_b.add_dot(i, j)

                    target_len = len([i for i in splits if i.line.a.x is not None]) * 2

                    if len(a_shape.sub_name) == target_len:
                        self.__add_offset_x_y(a_shape)
                        self.__add_offset_x_y(b_shape)

                self.split_shapes = self.split_shapes + [a_shape, b_shape]

        self.__shapes_set_offsets(self.split_shapes)
        for s in self.parts_property.copy():
            if len(s) != len(self.split_shapes[0].sub_name):
                self.parts_property.pop(s)

        if self.split_shapes.__contains__(self):
            copy_split_shapes = self.split_shapes.copy()
            self.split_shapes = []
            return copy_split_shapes

        valid_shapes_names = [i.sub_name for i in self.split_shapes if sum([len(lay.x) for lay in i.layers])]
        self.split_shapes = [i for i in self.split_shapes if i.sub_name in valid_shapes_names]
        self.parts_property = {k: v for k, v in self.parts_property.items() if k in valid_shapes_names}

        return self.split_shapes

    def swap_layer(self, index_a: int, index_b: int):
        range_layers = range(len(self.layers))
        if index_a in range_layers and index_b in range_layers:
            self.layers[index_a], self.layers[index_b] = self.layers[index_b], self.layers[index_a]
            self.layers[index_a].z, self.layers[index_b].z = self.layers[index_b].z, self.layers[index_a].z

    def get_as_dict(self) -> dict:
        self.delete_secondary_surface()
        return super(Shape, self).get_as_dict()
