from functools import partial
from os import environ

from PyQt5 import uic, QtGui
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator, QIcon
from PyQt5.QtWidgets import QMainWindow, QPushButton, QLabel, QRadioButton, QComboBox, QDialog

from InputLogs.mvc.Model.log_curves import Log, ExpressionLog
from InputLogs.mvc.Model.map import Map
from InputLogs.mvc.Model.map_property import cut_along
from InputLogs.mvc.View.help_veiws import LogCreateHelp
from InputLogs.mvc.View.trend_view import TrendView
from res.strings import ErrorMessage, Tips, SelectionMessage, special_logs_name
from utils.create_layout import create_frame, clear_layout
from utils.file import FileEdit, mass_from_xlsx
from utils.pyqt_mods.clicked_label import ClickableLabel
from utils.pyqt_mods.selection_window import SelectionWindow


class CreateLog(QMainWindow):
    def __init__(self, data_map: Map):
        super(CreateLog, self).__init__()
        uic.loadUi(environ['project'] + '/ui/create_log_window.ui', self)
        self.setWindowIcon(QIcon(environ['project'] + 'res/pictures/InputLogo.png'))
        self.data_map = data_map
        self.oil_water_name = ''
        self.handlers()
        self.add_tips()
        self.update()

        self.excelFrame.hide()
        self.rangeFrame.hide()
        self.calcFrame.hide()

    def handlers(self):
        self.actionMain.triggered.connect(self.help_show)

        self.chooseLogFile.clicked.connect(self.choose_log_from_xlsx)
        self.oilCurveCheckBox.clicked.connect(partial(self.change_name_oil_water_type, 'O'))
        self.waterCurveCheckBox.clicked.connect(partial(self.change_name_oil_water_type, 'W'))

        self.rangeRadioButton: QRadioButton = self.rangeRadioButton
        self.rangeRadioButton.clicked.connect(self.type_curve_change)
        self.calculatedRadioButton.clicked.connect(self.type_curve_change)

        input_validator = QRegExpValidator(QRegExp("[^| ]{1,}"), self.nameLineEdit)
        self.nameLineEdit.setValidator(input_validator)

        for name in [''] + sorted(self.data_map.main_body_names()):
            self.layerNameComboBox.addItem(name)

        self.addCalculatedButton.clicked.connect(self.add_calculated_curve)
        self.addIntervalButton.clicked.connect(self.add_log_interval)

        self.curvesNameComboBox.textActivated.connect(self.add_curves_to_formula)

    def add_tips(self):
        self.waterCurveCheckBox.setToolTip(Tips.CreateWaterLog)
        self.oilCurveCheckBox.setToolTip(Tips.CreateOilLog)
        self.nameLineEdit.setToolTip(Tips.CreateNameLog)

        self.addIntervalButton.setToolTip(Tips.CurvesAddRangeCurve)

        self.calcFrame.setToolTip(Tips.CreateCalcLog)
        self.curvesNameComboBox.setToolTip(Tips.CurvesVarLog)
        self.addCalculatedButton.setToolTip(Tips.CurvesAddCalculatedCurve)
        # self.setToolTip(Tips.CreateLog)

    def help_show(self):
        self.help = LogCreateHelp()
        self.help.show()

    def type_curve_change(self):
        if self.rangeRadioButton.isChecked():
            self.rangeFrame.show()
            self.calcFrame.hide()
        else:
            self.calcFrame.show()
            self.rangeFrame.hide()

    def add_curves_to_formula(self):
        self.formulaLineEdit.setText(
            self.formulaLineEdit.text() + '{' + self.curvesNameComboBox.currentText() + '}')

    def change_name_oil_water_type(self, name: str):
        if name == 'O' and self.oilCurveCheckBox.isChecked():
            self.oil_water_name = '|O|'
            self.waterCurveCheckBox.setCheckState(False)
        elif name == 'W' and self.waterCurveCheckBox.isChecked():
            self.oil_water_name = '|W|'
            self.oilCurveCheckBox.setCheckState(False)
        else:
            self.oil_water_name = ''

    def open_trend_window(self, log: Log):
        if hasattr(self, 'trend_window'):
            self.trend_window.close()

        self.trend_window = TrendView(log)
        self.trend_window.show()
        self.trend_window.closeEvent = lambda _: self.update()

    def get_log_name(self):
        name = self.nameLineEdit.text()
        log_name = f'{name}|{self.layerNameComboBox.currentText()}|{self.oil_water_name}|'
        while log_name.__contains__('||'):
            log_name = log_name.replace('||', '|')
        return log_name

    def add_log_interval(self):
        log_name = self.get_log_name()
        if len(log_name) > 0:
            min_value, max_value = self.minValueSpinBox.value(), self.maxValueSpinBox.value()
            label_change_color(self.expressionValidLabel, 'red')
            if min_value >= max_value:
                self.expressionValidLabel.setText(ErrorMessage.MinMaxValid)
                return
            if len(log_name) <= 1:
                self.expressionValidLabel.setText(ErrorMessage.EmptyName)
                return
            self.data_map.add_logs(Log(self.data_map, name=log_name, min=min_value, max=max_value))
            self.update()

    def delete_log(self, name: str):
        self.data_map.pop_logs(name)
        self.update()

    def set_log_info(self, log: Log):
        if log.min is not None:
            self.minValueSpinBox.setValue(log.min)
            self.rangeRadioButton.click()
        if log.max is not None:
            self.maxValueSpinBox.setValue(log.max)
        if log.name is not None:
            self.nameLineEdit.setText(cut_along(log.name, '|'))
        if log.text_expression:
            self.formulaLineEdit.setText(log.text_expression)
            self.calculatedRadioButton.click()
        if log.name.__contains__('|O|'):
            self.oilCurveCheckBox.click()
        elif log.name.__contains__('|W|'):
            self.waterCurveCheckBox.click()
        if log.facia != '':
            self.layerNameComboBox.setCurrentText(log.facia)
        else:
            self.layerNameComboBox.setCurrentText('')

    def create_frames_log(self):
        widgets = []
        for log in sorted(self.data_map.all_logs, key=lambda i: i.name):
            widgets.append([])
            del_btn = QPushButton('❌')
            del_btn.setMaximumWidth(30)
            del_btn.clicked.connect(partial(self.delete_log, log.name))
            widgets[-1].append(del_btn)

            if not log.get_text().__contains__('xlsx'):
                trend_btn = QPushButton('⚡')
                trend_btn.setMaximumWidth(30)
                trend_btn.clicked.connect(partial(self.open_trend_window, log))
                widgets[-1].append(trend_btn)

            qlbl = ClickableLabel(log.get_text())
            qlbl.clicked.connect(partial(self.set_log_info, log))
            widgets[-1].append(qlbl)

        create_frame(self.logsScrollArea, widgets)

    def update(self):
        clear_layout(self.logsScrollArea)
        self.curvesNameComboBox.clear()

        for curve_name in sorted(self.data_map.main_logs_name_owc()) + special_logs_name:
            self.curvesNameComboBox.addItem(curve_name)
        self.create_frames_log()

    def _add_calculated_curve(self):
        options = [('Обновить старую', self.__add_calculated_curve),
                   ('Добавить новую', self.__add_calculated_curve)]

        self.selection_window = SelectionWindow(SelectionMessage.UpdateOrCreate, options)
        self.selection_window.show()

    def add_calculated_curve(self):
        expr_log = ExpressionLog(self.data_map, self.formulaLineEdit.text())
        if expr_log():
            self.expressionValidLabel.setText(self.formulaLineEdit.text() + ' ok')
            label_change_color(self.expressionValidLabel, 'green')
            l = Log(self.data_map, name=self.get_log_name(), x=expr_log.x)
            l.text_expression = expr_log.text_expression
            self.data_map.add_logs(l)
        else:
            label_change_color(self.expressionValidLabel, 'red')
            self.expressionValidLabel.setText(self.formulaLineEdit.text() + ' error')
        self.update()

    def choose_log_from_xlsx(self):
        text = FileEdit(self).open_file('xlsx')
        for k, v in mass_from_xlsx(text).items():
            text += f'{k}\n{v}\n'
            self.data_map.add_logs(Log(name=k, x=v))
        self.fileTextBrowser.setText(text)
        self.update()


def label_change_color(lbl: QLabel, color: str):
    pal = lbl.palette()
    pal.setColor(QtGui.QPalette.WindowText, QtGui.QColor(color))
    lbl.setPalette(pal)
