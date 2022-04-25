from os import environ
from typing import Callable

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget


class SingleLayWidget(QWidget):
    def __init__(self, index: int, z: int = 0, edit_lay_handler: Callable = None):
        super(SingleLayWidget, self).__init__()
        uic.loadUi(environ['input_data']+'/ui/mini_surface.ui', self)
        self.edit_lay: () = edit_lay_handler
        self.index = index
        self.heightLineEdit.setText(str(z))
        self.pre_value_height = z
        self.handlers_connect()

    def handlers_connect(self):
        self.addPreButton.clicked.connect(self.add_pre_lay)
        self.addPostButton.clicked.connect(self.add_post_lay)
        self.delButton.clicked.connect(self.del_lay)
        self.moveUpButton.clicked.connect(self.move_up)
        self.moveDownButton.clicked.connect(self.move_down)
        self.heightLineEdit.textChanged.connect(self.textChanged)
        self.heightLineEdit.editingFinished.connect(self.textAccepted)

    def textChanged(self, text):
        value = int('0' + ''.join(list(filter(str.isdigit, text))))
        self.heightLineEdit.setText(str(value))

    def textAccepted(self):
        if self.pre_value_height != int('0' + ''.join(list(filter(str.isdigit, self.heightLineEdit.text())))):
            self.pre_value_height = int('0' + ''.join(list(filter(str.isdigit, self.heightLineEdit.text()))))
            self.edit_lay(self.index, 'change_height', height=self.pre_value_height)
            self.heightLineEdit.setText(str(self.pre_value_height))

    def move_up(self):
        self.edit_lay(self.index, 'move_up')

    def move_down(self):
        self.edit_lay(self.index, 'move_down')

    def add_pre_lay(self):
        self.edit_lay(self.index)

    def add_post_lay(self):
        self.edit_lay(self.index, 'add_post')

    def del_lay(self):
        self.edit_lay(self.index, 'del')
