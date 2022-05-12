import os
from typing import Final


class MetaConst(type):
    def __setattr__(cls, name, value):
        pass


class Const(metaclass=MetaConst):
    pass


def main_icon() -> str:
    return os.environ['project'] + '/res/pictures/InputLogo.png'


class Limits(Const):
    MAX_TREND_RATIO: Final = 1
    MAX_HEIGHT: Final = 500
    MIN_HEIGHT: Final = 0
    WIDTH: Final = 25
    LENGTH: Final = 25
    BASE_PLOT_SCALE: Final = 25


class TitleName:
    RoofExportDialog: Final = 'Roof export'
    RoofProfileEditWindow: Final = 'Roof profile'
    ShapeEditWindow: Final = 'InputData'
    SplitEditWindow: Final = 'Split'
    ViewingLayersWindow: Final = 'Choose surface'
    SurfaceEditWindow: Final = 'Surface'
    InputLogView: Final = 'InputLogs'


class ErrorMessage(Const):
    MinMaxValid: Final = 'Min should be less than max'
    EmptyName: Final = 'The name cannot be empty'


class Tips(Const):
    SIMPLIFY_BUTTON: Final = "Раставляет точки по периметру линии \n" \
                            "равно удаленно друг от друга"

    CreateWaterLog: Final = "Нужно выбрать если кривая будет применяться к Водной части фации"

    CreateOilLog: Final = "Нужно выбрать если кривая будет применяться к Нефтяной части фации"

    CreateLog: Final = "Можно добавить два типа кривых:\n" \
                       "Первый тип - задаеться минимумом и максимумом.\n" \
                       "В нем точки для кривой будут генерироваться " \
                       "рандомно в заданом диапазоне." \
                       "\n\n" \
                       "Второй тип - вычисляемая кривая она вычисляеться на основе кривой(кривых)" \
                       " первого типа и заданного уравнения"

    CreateNameLog: Final = 'Обозначение кривой состоит из имени,\n' \
                           'приндлежности к воде или нефти и приндлежности к фации'

    CreateCalcLog: Final = 'В выражении можно использовать следующие знаки:' \
                           ' .,+,-.*./,(,),**. ** - степень.\n' \
                           'Пример - ({y1|}+{y2|}-{y|Clay|W|}*{y3|}/2)*1.5'

    CurvesVarLog: Final = 'Выбирите чтобы добавить в выражение переменную'

    CurvesAddCalculatedCurve: Final = 'Добавить кривую Calculated Curve'

    CurvesAddRangeCurve: Final = 'Добавить кривую Range Curve'

    ChooseLayer: Final = 'Изменить видимые слои'

    AddLogWindow: Final = 'Создать кривые'

    CreateCoreSampleWindow: Final = 'Добавить кривые имитирующие керн'

    CreateOWCWindow: Final = 'Указать ВНК для фаций'

    AttachLogWindow: Final = 'Связать кривые и фации'

    LogSelect: Final = 'Изменить отображаемую кривую'
