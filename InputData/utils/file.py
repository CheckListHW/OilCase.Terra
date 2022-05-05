import os
from os import getcwd
from typing import Final, Optional

from PyQt5.QtWidgets import QFileDialog, QInputDialog, QWidget, QMessageBox

from utils.filedialog import save_dict_as_json


class FileEdit:
    # Messages
    create_file_default: Final = 'Введите название файла:'
    create_project_default: Final = 'Введите название проекта:'
    create_file_error: Final = 'Не удалось создать файл,  \nфайл с таким именем уже существует'
    data_model_name = 'data.model'

    def __init__(self, parent: QWidget, file_used=''):
        self.parent = parent
        self.project_path = file_used
        self.model_path = ''

    def save_model_file(self, data):
        if not self.model_path:
            self.create_project()
        save_dict_as_json(data=data, path=self.project_path, filename=self.model_path)

    def save_file(self, data: dict):
        if not self.project_path:
            self.create_file()
        save_dict_as_json(data=data, filename=self.project_path)

    def open_file(self):
        self.project_path, _ = QFileDialog.getOpenFileName(self.parent, '', getcwd(), 'Json Files (*.json)')
        return self.project_path

    def create_file(self, msg=None, filename: str = None) -> str:
        if not msg:
            msg = self.create_file_default

        if filename:
            return QFileDialog.getExistingDirectory(self.parent, getcwd()) + f'/{filename}'

        filename, ok = QInputDialog.getText(self.parent, 'Input Dialog', str(msg))
        if ok and filename and filename != '':
            path = QFileDialog.getExistingDirectory(self.parent, getcwd())
            self.project_path = save_dict_as_json({}, path, filename)
            return self.project_path
        return ''

    def open_project(self):
        self.project_path = QFileDialog.getExistingDirectory(self.parent, '', getcwd())
        if self.project_path:
            self.model_path = self.project_path + '/' + FileEdit.data_model_name
            return self.project_path

    def create_project(self) -> Optional[str]:
        name, ok = QInputDialog.getText(self.parent, 'Input Dialog', str(FileEdit.create_project_default))
        if not ok or name == '':
            return

        project_name = f'/{name.replace(" ", "_")}.oilcase'
        self.project_path = QFileDialog.getExistingDirectory(self.parent, getcwd()) + project_name

        try:
            os.mkdir(self.project_path)
            self.model_path = save_dict_as_json({}, self.project_path, 'data.model')
            return self.project_path
        except FileExistsError as e:
            msg = QMessageBox()
            msg.setWindowTitle("Project create error")
            msg.setText(str(e))
            msg.exec_()


