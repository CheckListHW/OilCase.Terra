import math

import numpy as np
from matplotlib import pyplot as plt

from InputData.mvc.Controller.qt_matplotlib_connector import EditorController
from InputData.mvc.Model.map import Map
from InputData.mvc.Model.shape import Shape
from utils.geometry.point_in_polygon import check_polygon_in_polygon
from utils.geometry.prepare_layers_for_plot_3d import data_for_plot_3d
from utils.geometry.simplify_line import simplify_line
from utils.transform_data_to_export import dict_update, transform_data


class Plot3d:
    __slots__ = 'fig', 'ax', 'connector'

    def __init__(self, connector: EditorController = None):
        if connector is None:
            self.fig = plt.figure()
            self.ax = self.fig.add_subplot(111, projection='3d')
        else:
            self.connector = connector
            self.fig = connector.figure
            self.ax = connector.ax

    def draw(self):
        if hasattr(self, 'connector'):
            self.ax.invert_zaxis()
            self.connector.draw()


class DrawVoxels:
    def __init__(self, map_val: Map, plot3d=None):
        self.repeat = {}
        self.map = map_val
        self.all_polygon = np.zeros([1, 1, 1], dtype=bool)
        self.plot3d = plot3d if plot3d else Plot3d()

    def update_limits(self):
        x_size, y_size, z_size = self.map.size.x, self.map.size.y, self.map.size.z
        self.plot3d.ax.set_xlim3d(xmin=0.000001, xmax=x_size * 1.1)
        self.plot3d.ax.set_ylim3d(ymin=0.000001, ymax=y_size * 1.1)
        self.plot3d.ax.set_zlim3d(zmin=0.000001, zmax=z_size * 1.1)

    def redraw(self):
        if self.map.draw_speed == 'Polygon':
            self.draw_all_polygon()
        else:
            self.draw_plot()
        self.map.update_size()
        self.update_limits()
        self.plot3d.draw()

    def draw_plot(self):
        self.plot3d.ax.clear()
        shapes: [Shape] = self.map.get_visible_shapes()

        self.map.data = {}
        for shape in shapes:
            # roof_profile_offset
            r_p_o = self.map.roof_profile.get_x_y_offset(base=max(self.map.size.x, self.map.size.y))
            r_p_o = [[0 if shape.filler else j for j in i] for i in r_p_o]

            # include_not_primary
            i_n_t, _ = (True, shape.calc_intermediate_layers()) \
                if self.map.draw_speed == 'Simple' else (False, shape.delete_secondary_surface())

            main_layers = [lay for lay in shape.layers if (lay.primary or i_n_t) and lay.x != []]

            layers, layers_x, layers_y = [], [], []
            value = max([len(lay.scalable_curve[0]) for lay in main_layers] + [0])
            for lay in main_layers:
                a, b = simplify_line(lay.scalable_curve[0], lay.scalable_curve[1], value)
                layers_x.append(a)
                layers_y.append(b)
                layers.append((lay.z, a, b))

            if not layers_x:
                continue

            ceil: () = lambda i, m: int(sorted([0, i, m - 1])[1])

            layers_z = [[lay[0] + r_p_o[ceil(x1, self.map.size.x)][ceil(y1, self.map.size.y)]
                         for x1, y1 in zip(lay[1], lay[2])] for lay in layers]

            layers_x, layers_y, layers_z = data_for_plot_3d(layers_x, layers_y, layers_z)
            x, y, z = np.array(layers_x), np.array(layers_y), np.array(layers_z)
            color = '#%02x%02x%02x' % (shape.color[0], shape.color[1], shape.color[2])
            self.plot3d.ax.plot_surface(x, y, z, color=color, alpha=shape.alpha)

    def draw_all_polygon(self):
        self.plot3d.ax.clear()
        self.repeat, self.map.data, main_data, self.all_polygon = {}, {}, [], np.zeros([1, 1, 1],
                                                                                       dtype=bool)
        for shape in self.map.get_visible_shapes():
            shape.calc_intermediate_layers()
            data = self.calc_polygon_in_draw(shape)
            self.map.data[f'{shape.name}|{shape.sub_name}'] = dict_update(
                self.map.data.get(shape.name),
                transform_data(data))
            colors = np.empty(list(data.shape) + [4], dtype=np.float32)
            r, g, b = shape.color
            colors[:] = [r / 255, g / 255, b / 255, shape.alpha]
            main_data.append((data, colors))
        self.draw(main_data)

    def draw(self, main_data: []):
        for (data, colors), i in zip(main_data, range(len(main_data))):
            self.plot3d.ax.voxels(data, facecolors=colors)

    # set visible polygon
    def calc_polygon_in_draw(self, fig: Shape) -> []:
        roof = self.map.roof_profile.get_x_y_offset(base=max(self.map.size.x, self.map.size.y))
        roof = [[0 if fig.filler else j for j in i] for i in roof]
        z_size = int(fig.height + max(a for b in roof for a in b) + 1)

        data = np.zeros([self.map.size.x, self.map.size.y, z_size], dtype=bool)

        self.all_polygon.resize([max(x) for x in zip(data.shape, self.all_polygon.shape)])

        lay_size = fig.size.x * fig.size.y
        for lay in fig.layers:
            (x, y), lay_z = lay.scalable_curve, lay.z
            for x1 in range(fig.size.x):
                x1_c = math.ceil(x1)
                xx, rpo_x = [x1_c, x1_c + 1, x1_c, x1_c + 1], roof[x1]
                for y1 in range(fig.size.y):
                    y1_c = math.ceil(y1)
                    z1_offset, yy = int(lay_z + rpo_x[y1]), [y1_c, y1_c, y1_c + 1, y1_c + 1]
                    if check_polygon_in_polygon(x, y, xx, yy):
                        rep_name = lay_size * z1_offset + x1 * fig.size.y + y1
                        if self.repeat.get(rep_name) is None and 0 <= z1_offset <= fig.size.z:
                            self.repeat[rep_name] = True
                            data[x1, y1, z1_offset] = True

        return data
