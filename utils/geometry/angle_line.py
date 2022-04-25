import math
from typing import Tuple, List, Optional

from InputData.mvc.Model.point import Point


def reverse_dot(a: List[float], b: List[float]) -> Tuple[List[float], List[float]]:
    return [a[0], b[0]], [a[1], b[1]]


def line_angle_x_y(x: (float, float), y: (float, float)) -> float:
    a, b = reverse_dot(x, y)
    return line_angle_dot(a, b)


def line_angle_dot(dot_a: (float, float), dot_b: (float, float)) -> float:
    """ Return the angle between line and X axes (measured in radians). """
    a = min([dot_a, dot_b], key=lambda i: i[0])
    b = max([dot_a, dot_b], key=lambda i: i != a)
    c = [b[0], a[1]]

    b_len = line_distance_dot(a, c)
    c_len = line_distance_dot(a, b)
    return 0 if b_len == c_len else math.acos(b_len / c_len) * (1 if a[1] < b[1] else -1)


def line_distance_dot(a, b):
    x, y = reverse_dot(a, b)
    return line_distance_x_y(x, y)


def line_distance_x_y(x, y):
    return ((x[0] - x[1]) ** 2 + (y[0] - y[1]) ** 2) ** 0.5


def intersection_segment_dot(a: Point, b: Point, c: Point, d: Point, vector=False) \
        -> Tuple[Optional[float], Optional[float]]:
    if a.y - b.y == 0:
        a, b, c, d = c, d, a, b

    a1, a2 = a.y - b.y, c.y - d.y
    b1, b2 = b.x - a.x, d.x - c.x
    c1, c2 = a.x * b.y - b.x * a.y, c.x * d.y - d.x * c.y

    if b1 * a2 - b2 * a1 != 0:
        y = (c2 * a1 - c1 * a2) / (b1 * a2 - b2 * a1)
        x = (-c1 - b1 * y) / (a1 if a1 != 0 else 0.001)
        x, y = round(x * 1000) / 1000, round(y * 1000) / 1000
        # print(min(a.x, b.x) <= x <= max(a.x, b.x), min(a.x, b.x), x, max(a.x, b.x))
        # print(min(a.y, b.y) <= y <= max(a.y, b.y), min(a.y, b.y), y, max(a.y, b.y))
        # print(min(c.x, d.x) <= x <= max(c.x, d.x), min(c.x, d.x), x, max(c.x, d.x))
        # print(min(c.y, d.y) <= y <= max(c.y, d.y), min(c.y, d.y), y, max(c.y, d.y))
        # print(x, y)
        if min(a.x, b.x) - 0.01 <= x <= max(a.x, b.x) + 0.01 and min(a.y, b.y) - 0.01 <= y <= max(a.y, b.y) + 0.01 and \
                min(c.x, d.x) - 0.01 <= x <= max(c.x, d.x) + 0.01 and min(c.y, d.y) - 0.01 <= y <= max(c.y, d.y) + 0.01:
            return x, y
        if vector:
            return x, y
    return None, None
