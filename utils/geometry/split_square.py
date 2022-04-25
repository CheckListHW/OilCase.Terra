from InputData.mvc.Model.line_segment import PolygonalChain, LineSegment
from InputData.mvc.Model.point import Point
from utils.geometry.angle_line import intersection_segment_dot


def rectangle(x: float, y: float) -> PolygonalChain:
    return PolygonalChain([0, x, x, 0, 0], [0, 0, y, y, 0])


def split_square(square: PolygonalChain, line: LineSegment) -> (PolygonalChain, PolygonalChain, LineSegment):
    chain1, chain2, real_split_line = PolygonalChain(), PolygonalChain(), LineSegment(Point(), Point())

    d, first, counter = [square.dots[0].x, square.dots[0].y], False, 1

    for i, j in zip(square.get_x(), square.get_y()):
        c, d = d, [i, j]
        x1, y1 = intersection_segment_dot(line.a, line.b, Point(c[0], c[1]), Point(d[0], d[1]), vector=True)

        if x1 is not None and y1 is not None:

            if not (min(square.get_x()) <= x1 <= max(square.get_x()) and min(square.get_y()) <= y1 <= max(
                    square.get_y())):
                x1, y1 = None, None
            else:
                if real_split_line.a.x is None:
                    real_split_line.a.set(x1, y1)
                else:
                    real_split_line.b.set(x1, y1)

        # если поподает во вторую точку
        if x1 == d[0] and y1 == d[1]:
            counter -= 1
        elif (x1 is not None and y1 is not None) and counter > 0:
            first = not first
            counter = 0
            chain1.add_dot(x1, y1)
            chain2.add_dot(x1, y1)

        counter += 1
        if first:
            chain1.add_dot(i, j)
        else:
            chain2.add_dot(i, j)

    try:
        chain1.add_dot(chain1.dots[0].x, chain1.dots[0].y)
    except IndexError:
        pass
    try:
        chain2.add_dot(chain2.dots[0].x, chain2.dots[0].y)
    except IndexError:
        pass

    if real_split_line.a.y is not None and real_split_line.b.y is not None:
        if real_split_line.a.y > real_split_line.b.y:
            real_split_line.a, real_split_line.b = real_split_line.b, real_split_line.a
        if real_split_line.a.x > real_split_line.b.x:
            real_split_line.a, real_split_line.b = real_split_line.b, real_split_line.a

    return chain1, chain2, real_split_line
