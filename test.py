from PyQt5.QtWidgets import QApplication

from InputLogs.mvc.Model.map import Map

# x = Map(path='C:/Users/KosachevIV/PycharmProjects/Input/InputLogs/base.json')
# x.export.export()

import sys
import pickle
# ? import pickletools
from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")


        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setObjectName("groupBox")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setGeometry(QtCore.QRect(10, 20, 91, 16))
        self.label.setObjectName("label")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.groupBox)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 40, 191, 51))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.spinBoxX = QtWidgets.QSpinBox(self.verticalLayoutWidget)
        self.spinBoxX.setMaximum(295)
        self.spinBoxX.setObjectName("spinBoxX")
        self.verticalLayout.addWidget(self.spinBoxX)
        self.spinBoxY = QtWidgets.QSpinBox(self.verticalLayoutWidget)
        self.spinBoxY.setMaximum(275)
        self.spinBoxY.setObjectName("spinBoxY")
        self.verticalLayout.addWidget(self.spinBoxY)
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setGeometry(QtCore.QRect(10, 100, 91, 16))
        self.label_2.setObjectName("label_2")
        self.frame = QtWidgets.QFrame(self.groupBox)
        self.frame.setGeometry(QtCore.QRect(210, 40, 311, 291))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.radioButton = QtWidgets.QRadioButton(self.frame)
        self.radioButton.setGeometry(QtCore.QRect(0, 0, 82, 17))
        self.radioButton.setText("")
        self.radioButton.setObjectName("radioButton")
        self.checkBox = QtWidgets.QCheckBox(self.groupBox)
        self.checkBox.setGeometry(QtCore.QRect(70, 210, 70, 17))
        self.checkBox.setObjectName("checkBox")
        self.pbSave = QtWidgets.QPushButton(self.groupBox)
        self.pbSave.setGeometry(QtCore.QRect(17, 131, 75, 23))
        self.pbSave.setObjectName("pbSave")
        self.pbOpen = QtWidgets.QPushButton(self.groupBox)
        self.pbOpen.setGeometry(QtCore.QRect(17, 160, 75, 23))
        self.pbOpen.setObjectName("pbOpen")
        self.textEdit = QtWidgets.QTextEdit(self.groupBox)
        self.textEdit.setGeometry(QtCore.QRect(17, 189, 181, 16))
        self.textEdit.setObjectName("textEdit")
        self.gridLayout_2.addWidget(self.groupBox, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 551, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.groupBox.setTitle(_translate("MainWindow", "GroupBox"))
        self.label.setText(_translate("MainWindow", "Управление"))
        self.label_2.setText(_translate("MainWindow", "Конфигурация"))
        self.checkBox.setText(_translate("MainWindow", "CheckBox"))
        self.pbSave.setText(_translate("MainWindow", "Сохранить"))
        self.pbOpen.setText(_translate("MainWindow", "Загрузить"))


class Example(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.radioButton.setEnabled(False)
        self.spinBoxX.setPrefix("x=")
        self.spinBoxY.setPrefix("y=")
        self.spinBoxX.valueChanged.connect(self.on_changed_X_Y)
        self.spinBoxY.valueChanged.connect(self.on_changed_X_Y)
        self.pbSave.clicked.connect(self.on_save)
        self.pbOpen.clicked.connect(self.on_open)

        self.frame.setStyleSheet("background-color: #0aa;")
        self.radioButton.setStyleSheet("background-color: #f00;")

    def on_changed_X_Y(self):
        self.radioButton.move(self.spinBoxX.value(), self.spinBoxY.value())

    def on_open(self):
        name = QtWidgets.QFileDialog.getOpenFileName()[0]
        if not name:
            msg = QtWidgets.QMessageBox.information(
                self,
                'Внимание',
                'Выберите файл с данными!'
            )
            return
        file = open(name, 'rb')
        x = pickle.load(file)
        y = pickle.load(file)
        self.spinBoxX.setValue(x)
        self.spinBoxY.setValue(y)

    def on_save(self):
        name = QtWidgets.QFileDialog.getSaveFileName()[0]
        if not name:
            msg = QtWidgets.QMessageBox.information(
                self,
                'Внимание',
                'Выберите файл для сохранения!'
            )
            return
        file = open(name, 'wb')
        x = self.spinBoxX.value()
        y = self.spinBoxY.value()
        x1 = pickle.dump(x, file)
        y1 = pickle.dump(y, file)
        # NameError: name 'picktools' is not defined
        # ??? picktools.dis(x1)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec_())
