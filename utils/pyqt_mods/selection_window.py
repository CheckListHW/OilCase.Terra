from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton

option = (str, ())


class SelectionWindow(QWidget):
    def __init__(self, text: str, options: [option]):
        super(SelectionWindow, self).__init__()
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(QLabel(text))
        self.option_widget = QWidget()
        self.option_widget.setLayout(QHBoxLayout())
        self.layout().addWidget(self.option_widget)

        for o in options:
            self.add_an_option(o)

    def add_an_option(self, o: option):
        btn = QPushButton(o[0])
        btn.clicked.connect(o[1])
        self.option_widget.layout().addWidget(btn)