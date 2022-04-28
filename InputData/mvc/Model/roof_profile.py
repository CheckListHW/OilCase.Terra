import numpy as np
from scipy.interpolate import griddata

from utils.json_in_out import JsonInOut
from utils.geometry.nearst_dot import nearst_dot_index
from InputData.resource.digit_value import Limits


class RoofPoint(JsonInOut):
    __slots__ = 'x', 'y', 'z'

    def __init__(self, x: float = None, y: float = None, z: float = None, load_dict: dict = None):
        self.x = x
        self.y = y
        self.z = z
        self.change(x, y, z)
        if load_dict:
            self.load_from_dict(load_dict)

    def change(self, x: float, y: float, z: float = None):
        self.x = x
        self.y = y
        self.z = z if z is not None else self.z


class RoofProfile(JsonInOut):
    __slots__ = 'points', 'interpolate_method', 'values_corner_points'

    def __init__(self):
        self.interpolate_method = 'cubic'
        self.points: [RoofPoint] = list()
        self.values_corner_points = {'ll': 0, 'lr': 0, 'ul': 0, 'ur': 0}

    def add(self, x: float, y: float, z: float):
        self.points.append(RoofPoint(x, y, z))

    def pop(self, x, y):
        index = nearst_dot_index([p.x for p in self.points], [p.y for p in self.points], x, y)
        if index in range(len(self.points)):
            self.points.pop(index)

    def load_from_dict(self, load_dict: dict):
        super(RoofProfile, self).load_from_dict(load_dict)
        self.points = []
        for point_dict in load_dict.get('points'):
            self.points.append(RoofPoint(load_dict=point_dict))

    def get_x_y(self) -> ([float], [float]):
        return [p.x for p in self.points], [p.y for p in self.points]

    def get_x_y_offset(self, base: float) -> [[float]]:
        points = np.array([[0, 0], [0, base], [base, 0], [base, base]] +
                          [[p.x / Limits.BASEPLOTSCALE * base, p.y / Limits.BASEPLOTSCALE * base] for p in self.points])
        ll, lr, ul, ur = self.values_corner_points.values()
        val = np.array([ll, lr, ul, ur] + [p.z for p in self.points])
        grid_x, grid_y = np.mgrid[0:base:1, 0:base:1]
        return griddata(points, val, (grid_x, grid_y), method=self.interpolate_method)
