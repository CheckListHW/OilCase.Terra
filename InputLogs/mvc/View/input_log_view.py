import os
import time
from functools import partial
from os import environ
from threading import Thread

from PyQt5 import uic
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QPushButton, QLabel

from InputLogs.mvc.Controller.plot_controller import PlotController, PlotMapController, \
    PlotLogController
from InputLogs.mvc.Model.map import Map
from InputLogs.mvc.View.attach_log_view import AttachLogView
from InputLogs.mvc.View.create_core_sample_view import CreateCoreSampleView
from InputLogs.mvc.View.create_log_view import CreateLog
from InputLogs.mvc.View.owc_edit_view import OwcEditView
from InputLogs.mvc.View.setiings_view import SettingsView
from InputLogs.resourse.strings import TitleName, main_icon, Tips
from utils.file import FileEdit
from utils.log.log_file import read_log


class InputLogController:
    def __init__(self, controllers: [PlotController]):
        self.controllers = controllers

    def draw_all(self, data_map: Map):
        for controller in self.controllers:
            controller.re_draw(data_map)


class InputLogView(QMainWindow):
    def __init__(self, file_edit=FileEdit()):
        super(InputLogView, self).__init__()
        uic.loadUi(environ['project'] + '/ui/log_input_form.ui', self)

        self.setWindowTitle(TitleName.InputLogView)
        self.setWindowIcon(QIcon(main_icon()))

        self.text_log = ''
        self.file_edit = file_edit
        self.data_map: Map = Map()

        self.map_controller = PlotMapController(self.mapPlotWidget)
        self.map_controller.on_choose_column_observer.append(self.redraw_log)
        self.log_controller = PlotLogController(self.logPlotWidget)
        self.main_controller = InputLogController([self.map_controller, self.log_controller])

        self.handlers()
        self.set_tips()
        self.update_info()
        self.log_select()

        # x = Thread(target=partial(CreateCoreSampleView, self.data_map))
        # x.start()
        Thread(target=self.update_log).start()

    def showEvent(self, a0) -> None:
        super(InputLogView, self).showEvent(a0)
        if self.file_edit.log_path:
            self.__open_file()

    def set_tips(self):
        self.chooseLayerComboBox.setToolTip(Tips.ChooseLayer)
        self.chooseLogButton.setToolTip(Tips.AddLogWindow)
        self.createCoreSampleButton.setToolTip(Tips.СreateCoreSampleWindow)
        self.owcButton.setToolTip(Tips.СreateOWCWindow)
        self.attachLogButton.setToolTip(Tips.AttachLogWindow)
        self.logSelectComboBox.setToolTip(Tips.LogSelect)

    def hide_frame(self):
        self.toolsWidget.hide()

    def update_log(self):
        x = QPushButton()
        x.clicked.connect(self.__set_log)
        while True:
            time.sleep(3)
            x.click()

    def __set_log(self):
        text = str(read_log())
        if len(text) > 500:
            if text[-500:] != str(self.logText.toPlainText())[-500:]:
                text = text[-500:]
        else:
            if text != str(self.logText.toPlainText()):
                text = text
        self.set_log('\n'.join(list(text.split('\n').__reversed__()))[1:])

    def set_log(self, text: str):
        self.logText.setText(text)

    def update_info(self):
        self.chooseLayerComboBox.clear()
        self.chooseLayerComboBox.addItem('All')
        self.stepDepthLabel.setText(str(self.data_map.step_depth))
        self.initialDepthLabel.setText(str(self.data_map.initial_depth))

        for name in sorted(self.data_map.body_names):
            self.chooseLayerComboBox.addItem(name)

        self.logSelectComboBox.clear()
        for log_name in sorted(self.data_map.main_logs_name()):
            self.logSelectComboBox.addItem(log_name)

        self.redraw()

    def handlers(self):
        self.openFileAction.triggered.connect(self.open_file)
        self.saveFileAction.triggered.connect(self.save_file)
        self.exportSettingsAction.triggered.connect(partial(self.open_window, SettingsView))

        self.chooseLayerComboBox.activated.connect(self.choose_layer)
        self.chooseLogButton.clicked.connect(partial(self.open_window, CreateLog))
        self.owcButton.clicked.connect(partial(self.open_window, OwcEditView))
        self.attachLogButton.clicked.connect(partial(self.open_window, AttachLogView))
        self.createCoreSampleButton.clicked.connect(partial(self.open_window, CreateCoreSampleView))
        self.logSelectComboBox.activated.connect(self.log_select)

        self.actionTNavigator.triggered.connect(partial(self.export, 'tnav'))
        self.actionXLSX.triggered.connect(partial(self.export, 'xlsx'))
        self.actionCSV.triggered.connect(partial(self.export, 'csv'))
        self.actionUpdateData.triggered.connect(partial(self.export, 'update'))
        self.actionClearData.triggered.connect(partial(self.export, 'clear'))

    def update_export_data(self) -> None:
        self.exportMenu.setEnabled(False)
        self.export('clear')
        self.dataStatusLabel.setText('prepares...')
        self.data_map.export()
        self.dataStatusLabel.setText('Ready')
        self.exportMenu.setEnabled(True)

    def export(self, type: str = 'update'):
        if type == 'update':
            Thread(target=self.update_export_data).start()
            return None
        if type == 'clear':
            self.data_map.export_data = None
            self.dataStatusLabel: QLabel = self.dataStatusLabel
            self.dataStatusLabel.setText('Empty')
            return None

        if self.data_map.export.export is None:
            Thread(target=self.data_map.export.export).start()

        file_path = FileEdit(self).create_file(extension='')
        if file_path:
            Thread(target=partial(self.__export, type, file_path)).start()

    def __export(self, type_file: str, file_path: str):
        if type_file == 'csv':
            self.data_map.export.to_csv(file_path + 'csv')
        elif type_file == 'xlsx':
            self.data_map.export.to_xlsx(file_path + 'xlsx')
        elif type_file == 'tnav':
            self.data_map.export.to_t_nav(file_path + 'inc')
        else:
            self.data_map.export.to_csv(file_path + 'csv')

    def log_select(self):
        self.data_map.change_log_select(self.logSelectComboBox.currentText())
        self.redraw()

    def open_window(self, window: QMainWindow.__class__):
        if hasattr(self, 'sub_window'):
            self.sub_window.close()
            self.update_info()
        self.sub_window: QMainWindow = window(self.data_map)
        self.sub_window.show()
        self.sub_window.closeEvent = lambda a0: self.update_info()

    def save_file(self):
        self.file_edit.save_log(self.data_map.save())

    def open_file(self):
        self.file_edit.open_project()
        self.__open_file()

    def __open_file(self):
        self.toolsWidget.show()
        self.data_map.load(self.file_edit.polygon_model_path, self.file_edit.log_path)
        self.update_info()

    def redraw(self):
        self.main_controller.draw_all(self.data_map)

    def redraw_log(self, x: float, y: float):
        self.log_controller.draw_log(self.data_map, x, y)

    def choose_layer(self):
        select_layer = self.chooseLayerComboBox.currentText()
        self.data_map.visible_names = self.data_map.body_names if select_layer == 'All' else [
            select_layer]
        self.redraw()
