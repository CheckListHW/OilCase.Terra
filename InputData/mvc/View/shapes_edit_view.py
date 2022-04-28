from os import environ
from os.path import isfile

from PyQt5 import uic
from PyQt5.QtGui import QColor, QIcon
from PyQt5.QtWidgets import QMainWindow, QCheckBox, QColorDialog

from InputData.mvc.Controller.draw_shape import Plot3d, DrawVoxels
from InputData.mvc.Controller.qt_matplotlib_connector import EditorFigureController
from InputData.mvc.Model.map import Map, ExportMap
from InputData.mvc.Model.shape import Shape
from InputData.mvc.View.roof_export_dialog import RoofExportDialog
from InputData.mvc.View.roof_profile_view import RoofProfileEditWindow
from InputData.mvc.View.split_edit_view import SplitEditWindow
from InputData.mvc.View.surface_draw_view import SurfaceEditWindow
from InputData.resource.strings import main_icon, TitleName
from InputData.utils.file import FileEdit
from utils.filedialog import dict_from_json


class ShapeEditWindow(QMainWindow):
    def __init__(self):
        super(ShapeEditWindow, self).__init__()
        uic.loadUi(environ['project'] + '/ui/shape_edit.ui', self)

        self.setWindowTitle(TitleName.ShapeEditWindow)
        self.setWindowIcon(QIcon(main_icon()))
        self.hide_frame()

        self.map, self.file_edit = Map(), FileEdit(self)
        self.connector = EditorFigureController(self.viewFrame)
        self.voxels = DrawVoxels(self.map, Plot3d(self.connector))
        self.load_default_shape()
        self.handlers_connect()

        # self.map.attach(ObjectObserver([self.update_all]))
        self.set_size_info()
        self.update_all()
        # self.debug()

    def handlers_connect(self) -> None:
        self.create_file_action.triggered.connect(self.create_map)
        self.open_file_action.triggered.connect(self.open_map)
        self.exportRoofAction.triggered.connect(self.export_roof)
        self.exportMapAction.triggered.connect(lambda: FileEdit(self).save_file(ExportMap(self.map)()))
        self.save_file_action.triggered.connect(self.save_map)

        save_shape: () = lambda: self.file_edit.save_file(self.layersComboBox.currentData().get_as_dict)
        self.saveLayerButton.clicked.connect(save_shape)

        load_layer: () = lambda: self.layersComboBox.currentData().load_from_json(self.file_edit.open_file())
        self.loadLayerButton.clicked.connect(load_layer)

        self.deleteLayerButton.clicked.connect(self.delete_layer)

        self.addLayerButton.clicked.connect(self.add_layer)
        self.acceptSettingsButton.clicked.connect(self.accept_settings)
        self.editLayerButton.clicked.connect(self.edit_layer)
        self.updateButton.clicked.connect(self.update_all)
        self.acceptLayersChange.clicked.connect(self.accept_view)

        self.allLayersCheckBox.stateChanged.connect(self.change_all_layers_show)
        self.layersComboBox.activated.connect(self.update_layers_info)

        self.nameLineEdit.editingFinished.connect(self.accept_settings)
        self.priority_spinbox.editingFinished.connect(self.accept_settings)
        self.fillerCheckBox.stateChanged.connect(self.accept_filler)

        self.xEndSpinbox.editingFinished.connect(self.accept_size)
        self.xEndSpinbox.setValue(self.map.size.x_constraints.end)

        self.yEndSpinbox.editingFinished.connect(self.accept_size)
        self.yEndSpinbox.setValue(self.map.size.y_constraints.end)

        self.zStartSpinbox.editingFinished.connect(self.accept_size)
        self.zEndSpinbox.editingFinished.connect(self.accept_z_size)

        self.colorButton.clicked.connect(lambda: self.show_palette(self.set_color_shape))

        self.shapePartNameComboBox.activated.connect(self.update_part_info)

        self.split_handlers_connect()
        self.speedPlotDrawComboBox.activated.connect(self.change_draw_speed)

    def hide_frame(self):
        frames = [self.visibleFrame, self.propertyFrame, self.editFrame, self.partControlFrame,
                  self.funcFrame, self.sizeFrame, self.saveLoadShapeFrame]
        _ = [frame.hide() for frame in frames]

    def show_frame(self):
        frames = [self.visibleFrame, self.propertyFrame, self.editFrame, self.partControlFrame]
        _ = [frame.show() for frame in frames]

    def set_size_info(self):
        self.xEndSpinbox.setValue(self.map.size.x)
        self.yEndSpinbox.setValue(self.map.size.y)
        self.zEndSpinbox.setValue(self.map.size.z)

    def debug(self):
        self.edit_layer()

    def load_default_shape(self):
        base_dict = dict_from_json(environ['input_data'] + '/base.json')
        if base_dict != {}:
            self.file_edit.file_used = environ['input_data'] + '/base.json'
            self.map.load_from_dict(base_dict)

    def save_map(self):
        self.file_edit.save_file(self.map.get_as_dict())

    def create_map(self):
        self.change_map(self.file_edit.create_file())

    def open_map(self):
        self.change_map(self.file_edit.open_file())
        self.show_frame()

    def change_map(self, data_map_path: str):
        if isfile(data_map_path):
            self.map.load_from_json(data_map_path)
            self.set_size_info()
            self.update_all()

    def export_roof(self):
        self.roof_export = RoofExportDialog(self.map)
        self.roof_export.open()

    def delete_layer(self):
        self.map.delete_layer(figure=self.layersComboBox.currentData())
        self.update_all()

    def add_layer(self):
        self.propertyFrame.show()
        self.map.add_layer()
        self.update_all()

    def accept_z_size(self):
        self.accept_size()
        for shape in [shape for shape in self.map.shapes if shape.filler]:
            shape.set_filler(True)
        self.update_all()

    def change_draw_speed(self):
        self.map.draw_speed = self.speedPlotDrawComboBox.currentText()
        if self.map.draw_speed != 'Polygon':
            self.voxels.redraw()

    def change_part_offset(self):
        part_name: str = self.shapePartNameComboBox.currentText()
        for layer in self.map.get_shapes():
            if layer.parts_property.get(part_name):
                layer.parts_property.get(part_name).offset = self.partOffsetSpinBox.value()
        self.update_all()

    def split_handlers_connect(self):
        self.partOffsetSpinBox.editingFinished.connect(self.change_part_offset)

    def set_color_part(self, color: QColor):
        r, g, b, _ = color.getRgb()

        self.layersComboBox.currentData().split_controller. \
            change_part_color(int(self.partNumberComboBox.currentText()) - 1, [r, g, b])

    def set_color_shape(self, color: QColor):
        alpha = color.alpha() / 255
        r, g, b, _ = color.getRgb()
        shape: Shape = self.layersComboBox.currentData()
        shape.color = [r, g, b]
        shape.alpha = alpha
        self.update_all()

    def show_palette(self, handler):
        if self.layersComboBox.currentData():
            r, g, b = self.layersComboBox.currentData().color
            alpha = self.layersComboBox.currentData().alpha * 255
            cd = QColorDialog(QColor(r, g, b, alpha=alpha), self)
            cd.setOption(QColorDialog.ShowAlphaChannel, on=True)
            cd.colorSelected.connect(handler)
            cd.show()

    def accept_size(self):
        x_end, y_end, z_end = self.xEndSpinbox.value(), self.yEndSpinbox.value(), self.zEndSpinbox.value()
        self.map.size.change_constraints(None, x_end, None, y_end, None, z_end)

    def update_all(self):
        self.accept_size()
        self.update_layers_info()
        self.list_displayed_layers()
        self.voxels.redraw()

    def update_layers_info(self) -> None:
        current_index = self.layersComboBox.currentIndex() if self.layersComboBox.currentIndex() >= 0 else 0
        self.layersComboBox.clear()

        for layer in self.map.get_shapes():
            self.layersComboBox.addItem(layer.name, layer)

        self.layersComboBox.setCurrentIndex(current_index)

        layer: Shape = self.layersComboBox.currentData()
        if type(layer) is Shape:
            self.editLabel.setText('Edit ({0})'.format(layer.name))
            self.layerNameLabel.setText(layer.name)
            self.nameLineEdit.setText(layer.name)
            self.priority_spinbox.setValue(layer.priority)
            self.fillerCheckBox.setChecked(layer.filler)
            self.shapePartNameComboBox.clear()

        for part in {a for b in [list(layer.parts_property.keys()) for layer in self.map.get_shapes()] for a in b}:
            self.shapePartNameComboBox.addItem(part)

        self.update_part_info()

    def update_part_info(self):
        layer: Shape = self.layersComboBox.currentData()
        part_name: str = self.shapePartNameComboBox.currentText()
        try:
            self.partOffsetSpinBox.setValue(layer.parts_property.get(part_name).offset)
        except AttributeError:
            pass

    def list_displayed_layers(self):
        for i in reversed(range(self.showLayersScrollArea.count())):
            self.showLayersScrollArea.itemAt(i).widget().setParent(None)

        layers = self.map.get_shape_with_part()

        for i in range(len(layers)):
            widget = QCheckBox(layers[i].name + layers[i].sub_name)
            widget.setChecked(layers[i].visible)
            widget.setProperty('figure', layers[i])
            widget.stateChanged.connect(self.accept_view)
            self.showLayersScrollArea.addWidget(widget, i, 0)

    def change_all_layers_show(self, check):
        for lay in self.map.get_shapes():
            lay.visible = True if check else False
        self.update_all()

    def accept_view(self):
        for i in range(self.showLayersScrollArea.count()):
            check_box = self.showLayersScrollArea.itemAt(i).widget()
            if type(check_box) is QCheckBox:
                check_box.property('figure').visible = True if check_box.checkState() else False

        self.update_all()

    def edit_layer(self):
        # self.edit_window если оставлять локальной переменной удаляется из памяти!
        if self.layersComboBox.currentData() is None:
            return
        edit_text: str = self.editPropertyComboBox.currentText()
        if edit_text.__contains__('Surface'):
            self.edit_window = SurfaceEditWindow(shape=self.layersComboBox.currentData())
            self.visibleFrame.show()
        elif edit_text.__contains__('Split'):
            self.edit_window = SplitEditWindow(self.map)
            self.partControlFrame.show()
        elif edit_text.__contains__('Roof'):
            self.edit_window = RoofProfileEditWindow(self.map)
        else:
            return
        self.edit_window.show()

    def accept_settings(self):
        self.editFrame.show()
        self.layersComboBox.currentData().load_from_dict({'name': self.nameLineEdit.text(),
                                                          'filler': self.fillerCheckBox.isChecked(),
                                                          'priority': self.priority_spinbox.text()})
        self.update_layers_info()

    def accept_filler(self):
        self.layersComboBox.currentData().set_filler(self.fillerCheckBox.isChecked())
        self.update_all()
