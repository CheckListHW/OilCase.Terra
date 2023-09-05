import os
import sys
from traceback import format_exception

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout

from InputData.mvc.View.shapes_edit_view import ShapeEditWindow
from res.strings import main_icon
from InputLogs.mvc.View.input_log_view import InputLogView
from utils.file import FileEdit
from utils.log.log_file import print_log

os.environ['input_data'] = os.getcwd() + '/InputData'
os.environ['input_logs'] = os.getcwd() + '/Inputlogs'
os.environ['project'] = os.getcwd()

log_out: ()


def console_excepthook(exc_type, exc_value, exc_tb):
    tb = "".join(format_exception(exc_type, exc_value, exc_tb))
    print_log(tb)
    log_out(tb)
    print("error!:", tb)


class InputDataLogs(QWidget):
    def __init__(self):
        super(InputDataLogs, self).__init__()
        self.file_edit = FileEdit('C:/Users/KosachevIV/Desktop/OilCase/Tanopchinskaya_svita.oilcase')
        # self.file_edit = FileEdit()
        self.data_window = ShapeEditWindow(file_edit=self.file_edit)
        self.log_window = InputLogView(file_edit=self.file_edit)

        self.log_out = self.log_window.set_log

        btn_logs = QPushButton('InputLogs')
        btn_data = QPushButton('InputData')
        btn_open_project = QPushButton('Open project')
        btn_open_project.clicked.connect(self.open_project)
        btn_logs.clicked.connect(self.open_logs)
        btn_data.clicked.connect(self.open_data)

        self.setLayout(QHBoxLayout())
        self.layout().addWidget(btn_open_project)
        self.layout().addWidget(btn_data)
        self.layout().addWidget(btn_logs)
        self.setWindowTitle('Input')
        self.setWindowIcon(QIcon(main_icon()))
        self.setFixedSize(300, 70)

    def open_project(self):
        self.file_edit.open_project()
        project_name = self.file_edit.project_path.split("/")[-1]
        self.setWindowTitle(f'Input Project: {project_name}')

    def open_logs(self):
        self.log_window.show()

    def open_data(self):
        self.data_window.show()

    def closeEvent(self, a0) -> None:
        os._exit(1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    sys.excepthook = console_excepthook
    window = InputDataLogs()
    window.show()
    log_out = window.log_out
    sys.exit(app.exec_())

# if __name__ == '__main__':
#     x = Map(path='C:/Users/KosachevIV/PycharmProjects/Input/InputLogs/base.json')
#     x.export.export()
