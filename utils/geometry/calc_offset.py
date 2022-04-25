import math

from InputData.mvc.Model.line_segment import LineSegment
from utils.geometry.angle_line import line_angle_x_y


def calc_offset(offset_angle: int, line: LineSegment) -> (float, float):
    return __calc_offset(offset_angle, [line.a.x, line.b.x], [line.a.y, line.b.y])


def __calc_offset(offset_angle: int, x: (float, float), y: (float, float)) -> (float, float):
    if offset_angle == 0:
        return 0, 0
    offset_len = 1 / math.tan(math.radians(offset_angle))

    angle = -line_angle_x_y(x, y)
    sin_a, cos_a = math.sin(angle), math.cos(angle)

    rotate_x = [x1 * cos_a - y1 * sin_a for x1, y1 in zip(x, y)]
    rotate_y = [x1 * sin_a + y1 * cos_a for x1, y1 in zip(x, y)]

    offset_y = rotate_y[0] + offset_len
    sin_a, cos_a = math.sin(-angle), math.cos(-angle)

    return (rotate_x[0] * cos_a - offset_y * sin_a) - x[0], (rotate_x[0] * sin_a + offset_y * cos_a) - y[0]
