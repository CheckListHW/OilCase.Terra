from functools import partial
from random import random

import pandas as pd

from InputLogs.mvc.Model.log_curves import Log, sort_expression_logs, expression_parser
from InputLogs.mvc.Model.map_property import CoreSample, cut_along, MapProperty
from utils.a_thread import AThread
from utils.log.log_file import print_log
from utils.time_work import MyTimer


class ExportLogs:
    __slots__ = 'data_map', 'export_threads'

    def __init__(self, data_map: MapProperty):
        self.data_map = data_map
        self.export_threads = []

    def __call__(self, *args, **kwargs):
        self.export()

    def export_on_thread(self, export_method: callable, path: str):
        if self.data_map.export_data is None:
            print_log('please update data')
            return

        export_thread = AThread()
        export_thread.finished.connect(lambda: print_log('Finish export Excel'))
        export_thread.callback = partial(export_method, path)
        export_thread.start()
        self.export_threads.append(export_thread)

    def to_xlsx(self, path: str):
        self.export_on_thread(self.__to_xlsx, path)

    def __to_xlsx(self, path: str):
        save_to_excel(self.data_map.export_data, path)

    def to_csv(self, path: str):
        self.export_on_thread(self.__to_csv, path)

    def __to_csv(self, path: str):
        save_to_csv(self.data_map.export_data, path)

    def to_t_nav(self, path: str):
        self.export_on_thread(self.__to_t_nav, path)

    def __to_t_nav(self, path: str):
        save_to_t_nav(self.data_map.export_data, path)

    def export(self):
        print_log('Start transform data')

        self.data_map.export_data = None
        data_map = self.data_map.map_copy()

        r: () = lambda i: round(i, 5) if i is float else i

        coors, data = [(x1, y1) for x1 in range(data_map.max_x + 1) for y1 in
                       range(data_map.max_y + 1)], {}

        for log_name in data_map.main_logs_name_non_expression():
            data_map.change_log_select(log_name)
            for x, y in coors:
                MyTimer.check_start('curve')
                column = data_map.get_column_curve(x, y)
                MyTimer.check_finish('curve')
                for x1, lithology, y1 in (column.intervals if column else []):
                    for i in range(len(x1)):
                        ceil_name = f'{x}-{y}-{y1[i]}'
                        if not data.get(ceil_name):
                            data[ceil_name] = {'i': x + 1, 'j': y + 1,
                                               'index': y1[i], 'Lithology': lithology}
                        data[ceil_name][log_name] = r(x1[i])

        format_depth: () = lambda ind: ind * self.data_map.step_depth + self.data_map.initial_depth
        data = add_height_above_fwl(data, data_map.owc)
        data = index_to_depth(data, format_depth)
        data = add_log_expression_in_export(data, data_map.attach_logs)
        data = edit_lithology_name_in_data(data)
        data = add_log_sample_in_export(data, data_map.core_samples,
                                        self.data_map.percent_safe_core)
        print_log('Data ready')
        self.data_map.export_data = data


def index_to_depth(data: {}, depth: ()) -> {}:
    for values in data.values():
        values['old_index'] = values['index']
        values['index'] = depth(values['index'])
    return data


def add_height_above_fwl(data: {}, owc: [{str: float}]) -> {}:
    for values in data.values():
        owc_level = owc.get(values['Lithology'].replace('O|', '').replace('W|', ''))
        if owc_level is not None:
            if values['index'] < owc_level:
                values['HeightAboveFWL'] = owc_level - values['index']
                values['Lithology'] = values['Lithology'] + 'O|'
                continue
            else:
                values['Lithology'] = values['Lithology'] + 'W|'
        values['HeightAboveFWL'] = 0
    return data


def edit_lithology_name_in_data(data: {}) -> {}:
    for values in data.values():
        values['Lithology'] = cut_along(values['Lithology'], '|')
    return data


def add_log_expression_in_export(data: dict, logs: {str: [Log]}) -> dict:
    expressions = {}
    expression_logs = list({l for l in [a for b in logs.values() for a in b]
                            if expression_parser(l.text_expression) is not None})

    sorted_expression_logs_name = sort_expression_logs(expression_logs)

    texts_expressions = []
    for lay_name, v in logs.items():
        for log in v:
            expr = expression_parser(log.text_expression)
            if expr is None:
                continue
            log_name = cut_along(log.name, '|')
            expressions[log_name] = {} if not expressions.get(log_name) else expressions[log_name]
            expressions[log_name][lay_name] = expr
            if lay_name.__contains__('|O|') or lay_name.__contains__('|W|'):
                expressions[log_name][lay_name.replace('O|', '').replace('W|', '')] \
                    = expr
            else:
                expressions[log_name].update({lay_name + 'O|': expr,
                                              lay_name + 'W|': expr})

            texts_expressions.append(log.text_expression)

    for log_name_expression in sorted_expression_logs_name:
        short_log_name_expression = cut_along(log_name_expression, '|')
        exps = expressions[short_log_name_expression]
        for k, v in data.items():
            try:
                if exps.get(v['Lithology']):
                    v[short_log_name_expression] = exps[v['Lithology']](v)
                if v.get(short_log_name_expression) is None:
                    v[short_log_name_expression] = -9999
                    # print(v.get(short_log_name_expression))
                    # print(v, exps)
                    # print(short_log_name_expression, expressions)
                    # breakpoint()
            except KeyError or AttributeError as l:
                v[short_log_name_expression] = -9999
                # print(l)
                # print(v.get(short_log_name_expression))
                # print(v, exps)
                # print(short_log_name_expression, expressions)
                # print_log(f'{log_name_expression} ; {v.keys()} ; {v["Lithology"]}')
                # breakpoint()

    return data


def add_log_sample_in_export(data: dict, core_samples: [CoreSample], percent: float) -> dict:
    for k in data.keys():
        check_percent = random() > percent
        for name_core_sample, log_name, lithology, null_value in core_samples:
            data[k][name_core_sample] = null_value
            if check_percent:
                continue
            if data[k]['Lithology'] != lithology:
                continue
            if data[k].get(log_name) is None:
                continue
            data[k][name_core_sample] = data[k][log_name] * ((random() - 0.5) / 10 + 1)
    return data


def prepare_dataframe_to_save(data: dict) -> pd.DataFrame:
    columns_name = set([a for b in [list(v.keys()) for v in data.values()] for a in b])
    return pd.DataFrame([row for _, row in data.items()], columns=columns_name)


def save_to_t_nav(data: [], path: str):
    print_log('Start save TNavigator(.inc)')
    data_str = ''
    df: pd.DataFrame = prepare_dataframe_to_save(data).sort_values(by=['index', 'j']).drop(
        ['i', 'j', 'index', 'Lithology'], axis=1)
    for data_name, column in df.items():
        data_str += f'{data_name} '
        for value, i in zip(column, range(len(column))):
            if i % 7 == 0:
                data_str += '\n'
            try:
                value = round(float(value), 5)
            except:
                pass
            data_str += f"1*{value} "
        data_str += '/ \n'

    file = open(path, 'w+')
    file.write(data_str)
    file.close()
    print_log(f'Export to TNavigator (.inc) цis finish save to:{path}')
    print_log(f'Numer of ceil: {len(df)}')


def save_to_excel(data: [], path: str):
    print_log('Start save Excel (.xlsx)')
    prepare_dataframe_to_save(data).to_excel(path, sheet_name='all')
    print_log('Export to Excel(.xlsx) is finish save to:' + path)


def save_to_csv(data: [], path: str):
    print_log('Start save .csv')
    prepare_dataframe_to_save(data).to_csv(path, index=False, sep=';', decimal=',')
    print_log('Export to .csv is finish save to:' + path)
