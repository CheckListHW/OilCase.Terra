from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel

from InputLogs.resourse.strings import Tips


class HelpWidget(QWidget):
    def __init__(self):
        super(HelpWidget, self).__init__()
        self.setLayout(QHBoxLayout(self))
        self.setWindowTitle('Помощь')


class LogCreateHelp(HelpWidget):
    def __init__(self):
        super(LogCreateHelp, self).__init__()
        self.layout().addWidget(QLabel(Tips.CreateLog))
