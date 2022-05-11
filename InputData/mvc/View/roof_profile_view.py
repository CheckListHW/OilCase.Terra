import os
from functools import partial

from PyQt5 import uic
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QSpinBox

from InputData.mvc.Controller.edit_plot_modes import ModeStatus
from InputData.mvc.Controller.qt_matplotlib_connector import EditorRoofProfileController
from InputData.mvc.Model.map import Map
from InputData.mvc.View.surface_choose_view import ViewingLayersWindow
from InputData.resource.strings import main_icon, TitleName


class RoofProfileEditWindow(QMainWindow):
    def __init__(self, map_value: Map):
        super(RoofProfileEditWindow, self).__init__()
        uic.loadUi(os.environ['project'] + '/ui/roof_profile_edit.ui', self)

        self.setWindowTitle(TitleName.RoofProfileEditWindow)
        self.setWindowIcon(QIcon(main_icon()))

        self.map = map_value
        self.surface_editor = EditorRoofProfileController(map=self.map, parent=self.draw_polygon_frame)

        self.button_connect()
        self.surface_editor.update_plot()
        self.addDot.click()

    def button_connect(self):
        self.addDot.clicked.connect(lambda: self.change_mode(ModeStatus.AddDot))
        self.moveDot.clicked.connect(lambda: self.change_mode(ModeStatus.MoveDot))
        self.deleteDot.clicked.connect(lambda: self.change_mode(ModeStatus.DeleteDot))
        self.chooseDot.clicked.connect(lambda: self.change_mode(ModeStatus.ChooseDot))
        self.interpolateMethodComboBox.currentTextChanged.connect(self.method_change)
        self.threeDButton.clicked.connect(self.surface_editor.plot.show3d)
        self.heightSpinBox.editingFinished.connect(self.change_height)

        self.llCornerSpinBox.editingFinished.connect(partial(self.change_high_corner_point, 'll', self.llCornerSpinBox))
        self.ulCornerSpinBox.editingFinished.connect(partial(self.change_high_corner_point, 'ul', self.ulCornerSpinBox))
        self.lrCornerSpinBox.editingFinished.connect(partial(self.change_high_corner_point, 'lr', self.lrCornerSpinBox))
        self.urCornerSpinBox.editingFinished.connect(partial(self.change_high_corner_point, 'ur', self.urCornerSpinBox))

    def change_high_corner_point(self, corner: str, spinbox: QSpinBox):
        if self.map.roof_profile.values_corner_points.get(corner) is not None:
            self.map.roof_profile.values_corner_points[corner] = spinbox.value()
        self.surface_editor.update_plot()

    def method_change(self):
        self.map.roof_profile.interpolate_method = self.interpolateMethodComboBox.currentText()
        self.surface_editor.update_plot()

    def change_height(self):
        if self.surface_editor.plot.nearst_dot_index is None:
            return
        if len(self.map.roof_profile.points) > self.surface_editor.plot.nearst_dot_index:
            self.map.roof_profile.points[self.surface_editor.plot.nearst_dot_index].z \
                = self.heightSpinBox.value()
        self.surface_editor.update_plot()

    def change_mode(self, mode: ModeStatus):
        self.modeNameLabel.setText(f": {str(mode).replace('ModeStatus.', '')}")
        self.surface_editor.set_mode(mode)
        self.surface_editor.update_plot()
