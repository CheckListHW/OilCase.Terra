import os

from PyQt5 import uic
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow

from InputData.mvc.Controller.qt_matplotlib_connector import EditorSplitController
from InputData.mvc.Model.map import Map
from InputData.resource.strings import main_icon, TitleName


class SplitEditWindow(QMainWindow):
    def __init__(self, map: Map):
        super(SplitEditWindow, self).__init__()
        uic.loadUi(os.environ['project'] + '/ui/split_edit.ui', self)

        self.setWindowTitle(TitleName.SplitEditWindow)
        self.setWindowIcon(QIcon(main_icon()))

        self.splits = map.splits
        self.surface_editor = EditorSplitController(map, parent=self.draw_polygon_frame)


        self.update_info()
        self.button_connect()
        self.toolsFrame.hide()

    def current_split_number(self) -> int:
        return int(self.splitNumberComboBox.currentText()) - 1

    def button_connect(self):
        self.splitNumberComboBox.activated.connect(self.change_current_split)
        self.angleSpinBox.valueChanged.connect(
            lambda: self.splits[self.current_split_number()].__setattr__('angle', self.angleSpinBox.value()))
        self.depthSpinBox.valueChanged.connect(
            lambda: self.splits[self.current_split_number()].__setattr__('depth', self.depthSpinBox.value()))
        self.depthStartRadioButton.clicked.connect(
            lambda: self.splits[self.current_split_number()].__setattr__('from_start', True))
        self.depthEndRadioButton.clicked.connect(
            lambda: self.splits[self.current_split_number()].__setattr__('from_start', False))
        self.saveButton.clicked.connect(self.save)

    def update_info(self):
        split = self.splits[self.current_split_number()]

        self.depthStartRadioButton.setChecked(split.from_start)
        self.depthEndRadioButton.setChecked(not split.from_start)
        self.angleSpinBox.setValue(split.angle)
        self.depthSpinBox.setValue(split.depth)

    def change_current_split(self):
        self.update_info()
        self.surface_editor.plot.surface.current_split = self.current_split_number()

    def save(self):
        for line, split in zip(self.surface_editor.plot.surface.splits, self.splits):
            split.line = line

        self.surface_editor.shape.splits = self.splits
