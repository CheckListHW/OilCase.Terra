import json
import os
import random
from os import getcwd
from os.path import isfile
from typing import Final, Optional

import pandas as pd
from PyQt5.QtWidgets import QFileDialog, QInputDialog, QMessageBox


def dict_from_json(filename: str) -> dict:
    if isfile(filename):
        with open(filename) as f:
            return json.load(f)
    else:
        return {}


def mass_from_xlsx(path: str) -> dict:
    logs = {}
    xl = pd.ExcelFile(path)
    df = xl.parse(xl.sheet_names[0])
    for name in df.keys():
        logs[name] = list(df[name].values)
    return logs


def save_dict_as_json(data: dict, path: str = os.getcwd(),
                      filename: str = f'/temp_files/lay_name{random.randint(1, 1000)}') -> str:
    if path.__contains__('.json'):
        path_save = path
    elif filename.__contains__('.json'):
        path_save = filename
    elif filename.__contains__('.'):
        path_save = path+'/'+filename.split('/')[-1]
    else:
        path_save = path + f'/{filename}.json'
    path_save.replace("\\", '/')
    path_save.replace('//', '/')

    try:
        json_file = open(path_save, mode='x')
    except FileNotFoundError:
        os.mkdir(path_save.split('lay_name')[0])
        json_file = open(path_save, mode='x')
    except FileExistsError:
        json_file = open(path_save, mode='w')
    json.dump(data, json_file)
    json_file.close()
    return path_save


class FileEdit:
    # Messages
    create_project_default: Final = 'Введите название проекта:'
    create_file_default: Final = 'Введите название файла:'
    create_file_error: Final = 'Не удалось создать файл,  \nфайл с таким именем уже существует'
    data_log = 'log.log'
    data_model_name = 'data.model'
    data_polygon_model = 'polygon.model'

    def __init__(self, project_path=''):
        self.project_path = project_path

    @property
    def model_path(self):
        if os.path.isdir(self.project_path):
            if os.path.isfile(self.project_path + '/' + FileEdit.data_model_name):
                pass
            else:
                save_dict_as_json({}, self.project_path, FileEdit.data_model_name)
            return self.project_path + '/' + FileEdit.data_model_name
        return ''

    @property
    def polygon_model_path(self):
        if os.path.isdir(self.project_path):
            return self.project_path + '/' + FileEdit.data_polygon_model

    @property
    def log_path(self):
        if os.path.isdir(self.project_path):
            return self.project_path + '/' + FileEdit.data_log

    def save_log(self, data):
        if not self.log_path:
            self.open_project()
        if self.log_path:
            save_dict_as_json(data=data, path=self.project_path, filename=self.log_path)

    def save_model_file(self, data) -> str:
        if not self.model_path:
            self.create_project()
        if self.model_path:
            return save_dict_as_json(data=data, path=self.project_path, filename=self.model_path)
        else:
            return ''

    def save_polygon_model(self, data) -> str:
        if not self.polygon_model_path:
            self.create_project()
        if self.polygon_model_path:
            return save_dict_as_json(data=data, path=self.project_path,
                                     filename=self.polygon_model_path)
        else:
            return ''

    def save_file(self, data: dict):
        if not self.project_path:
            self.create_file()
        save_dict_as_json(data=data, filename=self.project_path)

    def open_file(self, file_extension='json'):
        self.project_path, _ = QFileDialog.getOpenFileName(None, '', getcwd(),
                                                        f'{file_extension} Files (*.{file_extension})')
        return self.project_path

    def create_file(self, message=None, extension: str = '.json') -> Optional[str]:
        if not message:
            message = self.create_file_default
        filename, ok = QInputDialog.getText(None, 'Input Dialog', str(message))
        if ok and filename and filename != '':
            path = QFileDialog.getExistingDirectory(None, getcwd())
            if extension != '.json':
                extension = extension.replace('.', '')
                if filename.__contains__('.'):
                    return f'{path}/{filename}'
                else:
                    return f'{path}/{filename}{"." + extension}'
            else:
                self.project_path = save_dict_as_json({}, path, filename)
                return self.project_path

        return None

    def open_project(self):
        self.project_path = QFileDialog.getExistingDirectory(None, '', getcwd())
        if self.project_path:
            return self.project_path

    def create_project(self) -> Optional[str]:
        name, ok = QInputDialog.getText(None, 'Input Dialog', str(FileEdit.create_project_default))
        if not ok or name == '':
            return

        project_name = f'/{name.replace(" ", "_")}.oilcase'
        self.project_path = QFileDialog.getExistingDirectory(None, getcwd()) + project_name

        try:
            os.mkdir(self.project_path)
            save_dict_as_json({}, self.project_path, 'data.model')
            return self.project_path
        except FileExistsError as e:
            msg = QMessageBox()
            msg.setWindowTitle("Project create error")
            msg.setText(str(e))
            msg.exec_()
