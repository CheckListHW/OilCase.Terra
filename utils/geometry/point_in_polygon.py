def check_point_in_polygon(curves_x: [float], curves_y: [float], x: float, y: float) -> bool:
    entry, j = False, len(curves_x) - 1

    for i in range(len(curves_x)):
        curv_y_j, curv_y_i = curves_y[j], curves_y[i]
        if curv_y_i < y <= curv_y_j or curv_y_j < y <= curv_y_i:
            curv_x_i = curves_x[i]
            if curv_x_i + (y - curv_y_i) / (curv_y_j - curv_y_i) * (curves_x[j] - curv_x_i) < x:
                entry = not entry
        j = i

    return entry


def check_polygon_in_polygon(curves_x: [float], curves_y: [float], x: [float], y: [float]) -> bool:
    entry = False
    for x1, y1 in zip(x, y):
        entry = check_point_in_polygon(curves_x, curves_y, x1, y1) or entry
        if entry:
            return entry

    return entry
