from matplotlib import pyplot as plt

import random


def intersection_point_horizontal_plane(a: [float, float, float],
                                        b: [float, float, float], height: int) -> (float, float, float):
    a1, b1, c1 = a[0] - b[0], a[1] - b[1], a[2] - b[2]

    if c1 == 0:
        return (a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2
    else:
        h1 = abs((height - a[2]) / c1)
        return a[0] - h1 * a1, a[1] - h1 * b1, a[2] - h1 * c1


if __name__ == '__main__':
    rand: () = lambda: random.randint(0, 15)
    random_int: () = lambda: random.randint(0, 15)

    x1 = [random_int(), random_int(), random_int()]
    x2 = [random_int(), random_int(), random_int()]

    h = random.randint(min(x1[2], x2[2]), max(x1[2], x2[2]))

    x, y, z = intersection_point_horizontal_plane(x1, x2, h)

    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')

    ax.plot([x1[0], x2[0]], [x1[1], x2[1]], [x1[2], x2[2]])
    ax.scatter([x1[0], x2[0]], [x1[1], x2[1]], [x1[2], x2[2]])
    ax.scatter([x], [y], [z])

    plt.show()
