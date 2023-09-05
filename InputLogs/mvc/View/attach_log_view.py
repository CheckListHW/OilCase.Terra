from functools import partial
from os import environ

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QLabel, QCheckBox, QPushButton, QWidget, QHBoxLayout, QFrame

from InputLogs.mvc.Model.map import Map
from InputLogs.mvc.Model.map_property import cut_along
from InputLogs.mvc.View.list_scroll_widget import ListScrollWidgets
from res.strings import main_icon
from utils.create_layout import create_frame, clear_layout
from utils.pyqt_mods.restore_scroll_position import restore_position_scroll


class AttachLogView(QMainWindow):
    def __init__(self, data_map: Map):
        super(AttachLogView, self).__init__()
        uic.loadUi(environ['project'] + '/ui/attach_log_window.ui', self)

        self.setWindowIcon(QIcon(main_icon()))

        self.ind = 0

        self.data_map = data_map
        self.attach_layers = set([])
        self.attach_logs = set([])
        self.handlers()
        self.update()
        self.create_frames_info()

    def handlers(self):
        self.addButton.clicked.connect(self.start_attach_logs)

    def start_attach_logs(self):
        for lay_name, log_name in [(lay, log) for lay in self.attach_layers
                                   for log in self.attach_logs]:
            self.data_map.attach_log_to_layer(log_name, lay_name)

        self.attach_layers = set([])
        self.attach_logs = set([])
        self.create_frames_info()

    def create_frames_info(self):
        clear_layout(self.infoFrame.layout())
        list_scroll = ListScrollWidgets(self.infoFrame)
        list_scroll.add_scroll([QLabel(name.replace('|', ' '))
                                for name in sorted(['All_logs'] + self.data_map.main_logs_name())])

        names = list({lay_name for lay_name, log_name in
                      sorted(self.data_map.attach_list(), key=lambda i: i[0])})

        sub_names = [lay_name[lay_name.index('|') + 1:]
                     for lay_name, log_name in self.data_map.attach_list()]
        sub_names = {cut_along(lay_name, '|') for lay_name in sub_names}.union({'!!!'})
        sub_names.discard('')

        get_main_name: callable = lambda name: sorted([name.replace(v, '') for v in sub_names],
                                                      key=lambda i: len(i))[0].replace('||', '|')

        name_groups = {get_main_name(name): {name.replace(a, b)
                                             for a in sub_names
                                             for b in sub_names
                                             if name.replace(a, b) in names}
                       for name in names}

        for main_lay_name in sorted(name_groups.keys()):
            widgets, skip_list = [], set()

            name_lbl = QLabel(main_lay_name.replace('|', ' '))
            name_lbl.setAlignment(Qt.AlignCenter)

            widgets = {name: QFrame(self) for name in self.data_map.main_logs_name()}
            widgets['A'] = name_lbl

            for lay_name, log_name in sorted(self.data_map.attach_list(), key=lambda i: i[1]):
                if (not get_main_name(lay_name).__contains__(main_lay_name)) \
                        or get_main_name(lay_name) + log_name in skip_list:
                    continue

                skip_list.add(get_main_name(lay_name) + log_name)
                log = self.data_map.get_logs_by_name(log_name)

                detach_list = [(sub_lay_name, log_name)
                               for sub_lay_name in name_groups[get_main_name(lay_name)]]

                del_btn = QPushButton('❌')
                del_btn.setMaximumWidth(30)
                del_btn.clicked.connect(partial(self.detach_log_list, detach_list))

                lbl = QLabel(f"{cut_along(log_name, '|').replace('|', ' ')}")

                w: QFrame = widgets[lbl.text()]
                if w.children():
                    w.layout().addWidget(del_btn)
                    del_btn.setToolTip(f'{log_name if log is None else log.get_text()}')
                else:
                    w.setLayout(QHBoxLayout(w))
                    w.setToolTip(f'{log_name if log is None else log.get_text()}')
                    w.layout().addWidget(lbl)
                    w.layout().addWidget(del_btn)
                    w.setFrameShadow(2)

            list_scroll.add_scroll(widgets[k] for k in sorted(widgets.keys()))


        if hasattr(self, 'frames_info'):
            restore_position_scroll(list_scroll, self.frames_info.horizontalScrollBar().value(),
                                    self.frames_info.verticalScrollBar().value())
        self.frames_info = list_scroll
        self.update()

    def create_frames_layers(self):
        widgets = []
        for name in self.data_map.main_body_names_owc():
            layer_check = QCheckBox()
            layer_check.setMaximumWidth(30)
            layer_check.clicked.connect(partial(self.add_layer, layer_check.checkState, name))
            widgets.append([layer_check, QLabel(name.replace('|', ' '))])

        create_frame(self.layersGridLayout, widgets)

    def create_frames_logs(self):
        clear_layout(self.logFrame.layout())
        list_scroll = ListScrollWidgets(self.logFrame)
        for main_log_name in sorted(self.data_map.main_logs_name()):
            widgets = []

            lbl = QLabel(main_log_name.replace('|', ' '))
            lbl.setAlignment(Qt.AlignCenter)
            widgets.append(lbl)

            for log in sorted(self.data_map.logs_without_sub(), key=lambda i: i.name):
                if not cut_along(log.name, '|') == main_log_name:
                    continue

                log_check = QCheckBox()
                log_check.setMaximumWidth(30)
                log_check.clicked.connect(partial(self.add_logs, log_check.checkState, log.name))

                lbl = QLabel(log.get_text().replace('|', ' '))
                lbl.setToolTip(f'{log.get_text()}')

                w = QWidget(self)
                w.setLayout(QHBoxLayout(w))
                w.layout().addWidget(log_check)
                w.layout().addWidget(lbl)
                widgets.append(w)

            list_scroll.add_scroll(widgets)

        if hasattr(self, 'frames_info'):
            restore_position_scroll(list_scroll, self.frames_logs.horizontalScrollBar().value())
        self.frames_logs = list_scroll

    def add_logs(self, state: (), name: str):
        if state():
            self.attach_logs.add(name)
        else:
            self.attach_logs = self.attach_logs - {name}

    def add_layer(self, state: (), name: str):
        if state():
            self.attach_layers.add(name)
        else:
            self.attach_layers = self.attach_layers - {name}

    def detach_log_list(self, detach_list: [(str, str)]):
        for log_name, lay_name in detach_list:
            self.detach_log(log_name, lay_name)
        self.create_frames_info()

    def detach_log(self, lay_name: str, log_name: str):
        self.data_map.detach_log_to_layer(log_name, lay_name)

    def update(self):
        self.create_frames_logs()
        self.create_frames_layers()
