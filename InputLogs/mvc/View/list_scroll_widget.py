from PyQt5.QtWidgets import QHBoxLayout, QWidget, QVBoxLayout, QScrollArea, QSizePolicy, QSpacerItem


class ListScrollWidgets(QScrollArea):
    def __init__(self, parent: QWidget):
        super(ListScrollWidgets, self).__init__(parent)
        if self.parent().layout() is None:
            self.parent().setLayout(QHBoxLayout(self))

        self.parent().layout().addWidget(self)
        self.setWidget(QWidget(self))
        self.widget().setLayout(QHBoxLayout(self))
        self.widget().layout().setContentsMargins(0, 0, 0, 0)
        self.widget().layout().setSpacing(0)
        self.setWidgetResizable(True)

        self.spacer = QWidget(self)
        self.spacer.setLayout(QHBoxLayout())
        self.spacer.layout().addStretch()
        self.widget().layout().addWidget(self.spacer)

    def add_scroll(self, widgets: [QWidget]):
        widgets_frame = QWidget()
        widgets_frame.setLayout(QVBoxLayout(widgets_frame))

        for widget in widgets:
            widget.setFixedHeight(40)
            widgets_frame.layout().addWidget(widget)

        widgets_frame.layout().setContentsMargins(9, 0, 3, 0)
        widgets_frame.setFixedWidth(200)
        widgets_frame.layout().addStretch()
        self.widget().layout().addWidget(widgets_frame)

        self.spacer.setParent(None)
        self.widget().layout().addWidget(self.spacer)
