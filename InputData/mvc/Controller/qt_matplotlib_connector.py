from typing import Optional

from PyQt5 import QtWidgets
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QFrame, QShortcut
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure

from InputData.mvc.Controller.edit_plot_modes import *
from InputData.mvc.Controller.draw_surface import EditSurface, EditRoofProfileSurface
from InputData.mvc.Model.lithological_model import LithologicalModel
from InputData.mvc.Model.lithology import Lithology
from InputData.mvc.Model.size import Size
from InputData.mvc.Model.surface import Surface
from utils.file import save_dict_as_json


class EditorController(FigureCanvasQTAgg):
    def __init__(self, mode: ModeStatus, surf: Surface):
        # при добавлении 'super().__init__()' крашится
        self.mode: ModeStatus = ModeStatus.Empty
        self.handler_move_id = None
        self.lithological_model: Optional[LithologicalModel] = None
        self.lithology: Optional[Lithology] = None

        self.ax = self.figure.add_subplot()
        self.plot = EditSurface(fig=self.figure, ax=self.ax, surf=surf)

        self.plot.update_plot()
        self.set_mode(mode)

        self.mpl_connect('button_press_event', self.on_click)
        self.mpl_connect('button_release_event', self.on_release)
        self.mpl_connect('pick_event', self.pick_event)

        QShortcut(QKeySequence('Ctrl+Z'), self).activated.connect(self.set_prev)
        QShortcut(QKeySequence('Ctrl+Shift+Z'), self).activated.connect(self.set_next)

    def set_prev(self):
        self.plot.surface.memento.get_prev()
        self.update_plot()

    def set_next(self):
        self.plot.surface.memento.get_next()
        self.update_plot()

    def change_lay(self, lay: Surface):
        self.plot.surface = lay
        self.plot.update_plot()
        self.draw()

    def halve_dot(self):
        self.plot.halve_dot_count()
        self.draw()

    def update_plot(self):
        self.plot.update_plot()
        self.draw()

    def set_mode(self, status: ModeStatus):
        if status == ModeStatus.DrawCurve:
            self.mode = DrawCurve(self.plot)
        elif status == ModeStatus.DeleteDot:
            self.mode = DeleteDot(self.plot)
        elif status == ModeStatus.AddDot:
            self.mode = AddDot(self.plot)
        elif status == ModeStatus.MoveDot:
            self.mode = MoveDot(self.plot)
        elif status == ModeStatus.AddSplit:
            self.mode = AddSplit(self.plot)
        elif status == ModeStatus.Empty:
            self.mode = Empty(self.plot)
        elif status == ModeStatus.ChooseDot:
            self.mode = ChooseDot(self.plot)
        elif status == ModeStatus.Preview:
            self.mode = Preview(self.plot, self.kwargs.get('preview_click_handler'))

    def on_click(self, event):
        self.handler_move_id = self.mpl_connect('motion_notify_event', self.on_move)
        self.mode.on_click(event)
        self.draw()

    def on_move(self, event):
        self.mode.on_move(event)
        self.draw()

    def on_release(self, event):
        self.mode.on_release(event)
        self.mpl_disconnect(self.handler_move_id)
        self.draw()


class EditorSplitController(EditorController):
    def __init__(self, lithological_model: LithologicalModel, parent=None, **kwargs):
        self.kwargs = kwargs
        fig = Figure(tight_layout=True)
        self.lithological_model = lithological_model

        FigureCanvasQTAgg.__init__(self, fig)
        self.mainLayout = QtWidgets.QGridLayout(parent)
        self.mainLayout.addWidget(self)

        surf = Surface(size=self.lithological_model.size)
        surf.splits = [split_line.line for split_line in lithological_model.splits]
        super(EditorSplitController, self).__init__(surf=surf, mode=ModeStatus.AddSplit)


class EditorRoofProfileController(EditorController):
    def __init__(self, lithological_model: LithologicalModel, parent=None, **kwargs):
        self.kwargs = kwargs
        fig = Figure(tight_layout=True)
        self.lithological_model = lithological_model

        FigureCanvasQTAgg.__init__(self, fig)
        self.mainLayout = QtWidgets.QGridLayout(parent)
        self.mainLayout.addWidget(self)

        surf = Surface(size=lithological_model.size)
        super(EditorRoofProfileController, self).__init__(surf=surf, mode=ModeStatus.AddDot)
        self.plot = EditRoofProfileSurface(fig=self.figure, ax=self.ax,
                                           roof_profile=lithological_model.roof_profile)
        self.set_mode(ModeStatus.AddDot)


class EditorSurfaceControllerTight(EditorController):
    def __init__(self, parent=None, surf: Surface = None, **kwargs):
        self.kwargs = kwargs
        fig = Figure()
        fig.subplots_adjust(left=-0.003, bottom=0, right=1, top=1, wspace=0, hspace=0)

        FigureCanvasQTAgg.__init__(self, fig)
        self.mainLayout = QtWidgets.QGridLayout(parent)
        self.mainLayout.addWidget(self)

        super().__init__(surf=surf, mode=ModeStatus.Preview)


class EditorFigureController(FigureCanvasQTAgg):
    def __init__(self, parent: QFrame):
        fig = Figure(tight_layout=True)

        FigureCanvasQTAgg.__init__(self, fig)
        self.mainLayout = QtWidgets.QGridLayout(parent)
        self.mainLayout.addWidget(self)
        self.mainLayout.addWidget(NavigationToolbar2QT(self, parent))
        self.ax = self.figure.add_subplot(111, projection='3d')


class EditorSurfaceController(EditorController):
    def __init__(self, parent, shape: Lithology, **kwargs):
        self.kwargs = kwargs
        fig = Figure(tight_layout=True)
        self.lithology: Lithology

        FigureCanvasQTAgg.__init__(self, fig)
        self.mainLayout = QtWidgets.QGridLayout(parent)
        self.mainLayout.addWidget(self)
        self.mainLayout.addWidget(NavigationToolbar2QT(self, parent))

        self.select_layer = 0
        super().__init__(surf=shape.layers[0], mode=ModeStatus.DrawCurve)
        self.set_shape(lithology=shape)

    def set_shape(self, path: str = None, lithology: Lithology = None):
        if path:
            self.lithology = Lithology(size=Size(), path=path)
        elif lithology:
            self.lithology = lithology
        self.change_lay(0)

    def edit_lay(self, index: int, edit_method: str = 'add', **kwargs):
        lay = None
        if edit_method[:3] == 'add':
            pre_lay = self.lithology.layers[index]
            lay = self.lithology.insert_layer(index + 1 if edit_method == 'add_post' else index)
            if lay:
                lay.x, lay.y = pre_lay.x.copy(), pre_lay.y.copy()

        elif edit_method == 'del':
            self.lithology.pop_layer(index)
            layers_range = range(0, len(self.lithology.layers))
            lay = self.lithology.layers[index] if index in layers_range else None

        elif edit_method == 'move_up':
            if self.lithology.swap_layer(index, index - 1):
                lay = self.lithology.layers[index - 1]

        elif edit_method == 'move_down':
            if self.lithology.swap_layer(index, index + 1):
                lay = self.lithology.layers[index + 1]

        elif edit_method == 'change_height' and kwargs.get('height') is not None:
            self.lithology.set_layer_z(index, kwargs.get('height'))

        if lay is None:
            lay = self.lithology.layers[0]

        self.change_lay(lay=lay)

    def change_lay(self, index: int = None, lay: Surface = None):
        if index in range(0, len(self.lithology.layers)):
            super(EditorSurfaceController, self).change_lay(self.lithology.layers[index])
        elif lay:
            super(EditorSurfaceController, self).change_lay(lay)

    def save(self):
        if hasattr(self, 'shape'):
            fig_dict = self.lithology.get_as_dict()
            save_dict_as_json(fig_dict)

    def simplify_line(self):
        self.plot.simplify_line()
        self.draw()
