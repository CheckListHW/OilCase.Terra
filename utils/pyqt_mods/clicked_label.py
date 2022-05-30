from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QLabel
from PyQt5.uic.properties import QtWidgets


class ClickableLabel(QLabel):
    clicked = pyqtSignal()

    def __init__(self, text=None):
        super(ClickableLabel, self).__init__(text=text)

    def mousePressEvent(self, QMouseEvent):
        self.clicked.emit()
        QLabel.mousePressEvent(self, QMouseEvent)
