from functools import partial
from threading import Thread
from time import sleep
from typing import Optional

from PyQt5.QtWidgets import QScrollArea, QPushButton


def restore_position_scroll(area: QScrollArea, x: Optional[int] = None, y: Optional[int] = None):
    btn = QPushButton()
    btn.clicked.connect(partial(click, area, x, y))
    Thread(target=btn.click).start()


def click(area: QScrollArea, x: Optional[int], y: Optional[int]):
    if x is not None:
        area.horizontalScrollBar().setValue(x)
    if y is not None:
        area.verticalScrollBar().setValue(y)
    print(x, y)
