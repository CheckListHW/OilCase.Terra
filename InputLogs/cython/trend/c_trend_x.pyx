# cython: language_level=3

import numpy as np

cdef ceil(i: float, max_trend: float):
    return i if -max_trend <= i <= max_trend else np.sign(i) * max_trend

cdef f_offset(i: int, y1: float, avg: float, max_trend, f_trend: ()):
        return

cdef f_y_limit(y: float, a: float, b: float):
        return y if a <= y <= b else f_y_limit(a + a - y, a, b) if a > y else f_y_limit(b + b - y, a, b)

cpdef trend(min_x: int, max_x: int, dispersion: float, len_x: int, f_trend: (), max_trend:float):
    cdef int len_y = len_x

    cdef float m_t = max_trend
    cdef float a = min_x
    cdef float b = max_x
    cdef float avg = abs(min_x - max_x) / 2
    cdef float des = dispersion
    cdef float last = (min_x + max_x) / 2

    cdef list y = []

    for _ in range(len_y):
        last = np.random.uniform(a + (last - a) * des, b - (b - last) * des)
        y.append(last)

    cdef int i = 0
    cdef float y1 = 0

    return [f_y_limit(y1 + avg * ceil(f_trend(i / len_y), m_t), a, b) for i, y1 in zip(range(len_y), y)]

