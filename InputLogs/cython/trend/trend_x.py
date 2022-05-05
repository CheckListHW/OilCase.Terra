import InputLogs.cython.trend.c_trend_x as c_t


def trend(min_x: int, max_x: int, dispersion: float, len_x: int, f_trend: (), max_trend: float) -> [float]:
    return c_t.trend(min_x, max_x, dispersion, len_x, f_trend, max_trend)
