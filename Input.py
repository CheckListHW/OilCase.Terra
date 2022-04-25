import os
import sys
from traceback import format_exception

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout

from InputData.mvc.View.shapes_edit_view import ShapeEditWindow
from InputLogs.mvc.View.input_log_view import InputLogView
from utils.log.log_file import print_log

os.environ['input_data'] = os.getcwd()+'/InputData'
os.environ['input_logs'] = os.getcwd()+'/Inputlogs'


log_out: ()


def console_excepthook(exc_type, exc_value, exc_tb):
    tb = "".join(format_exception(exc_type, exc_value, exc_tb))
    print_log(tb)
    log_out(tb)
    print("error!:", tb)


class InputDataLogs(QWidget):

    def __init__(self):
        super(InputDataLogs, self).__init__()
        self.log_window = InputLogView()
        self.data_window = ShapeEditWindow()
        global log_out
        log_out = self.log_window

        btn_logs = QPushButton('InputLogs')
        btn_data = QPushButton('InputData')
        btn_logs.clicked.connect(self.open_logs)
        btn_data.clicked.connect(self.open_data)

        self.setLayout(QHBoxLayout())
        self.layout().addWidget(btn_data)
        self.layout().addWidget(btn_logs)
        self.setFixedSize(300, 70)

    def open_logs(self):
        self.log_window.show()

    def open_data(self):
        self.data_window.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = InputDataLogs()
    window.show()
    sys.exit(app.exec_())
