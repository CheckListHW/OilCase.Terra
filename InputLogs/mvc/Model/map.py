from InputLogs.mvc.Model.map_export import ExportLogs
from InputLogs.mvc.Model.map_property import MapProperty


class Map(MapProperty):
    __slots__ = '_visible_names', 'max_y', 'all_logs', 'owc', 'max_z', 'settings', 'path_map', 'max_x', 'attach_logs', \
                'percent_safe_core', 'step_depth', 'initial_depth', 'body_names', 'core_samples', 'interval_data', \
                'columns', 'export'

    def __init__(self, path: str = None, data: dict = None):
        super(Map, self).__init__(path, data)
        self.export = ExportLogs(self)
