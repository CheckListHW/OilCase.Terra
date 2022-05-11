from __future__ import annotations

from typing import Optional

from utils.json_in_out import JsonInOut


class Point(JsonInOut):
    __slots__ = 'x', 'y', 'z'

    def __init__(self, x: Optional[Optional[float]] = None, y: Optional[float] = None,
                 z: Optional[float] = None, load_dict: dict = None):
        self.set(x, y, z)

        if load_dict:
            self.load_from_dict(load_dict)

    def set(self, x: Optional[float], y: Optional[float], z: Optional[float] = None):
        self.x = x
        self.y = y
        self.z = z

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.z == other.z
