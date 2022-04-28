import os
from typing import Final

from InputData.resource.const_class import Const


class Tips(Const):
    SIMPLIFYBUTTON: Final = "Раставляет точки по периметру линии \n" \
                            "равно удаленно друг от друга"

    CreateWaterLog: Final = "Нужно выбрать если кривая будет применяться к Водной части фации"

    CreateOilLog: Final = "Нужно выбрать если кривая будет применяться к Нефтяной части фации"

    CreateLog: Final = "Можно добавить два типа кривых:\nПервый тип - задаеться минимумом и максимумом." \
                       " В нем точки для кривой будут генерироваться рандомно в заданом диапазоне." \
                       "\n\n" \
                       "Второй тип - вычисляемая кривая она вычисляеться на основе кривой(кривых) первого типа" \
                       "и заданного уравнения"

    CreateNameLog: Final = 'Обозначение кривой состоит из имени,\n' \
                           'приндлежности к воде или нефти и приндлежности к фации'

    CreateCalcLog: Final = 'В выражении можно использовать следующие знаки: .,+,-.*./,(,),**. ** - степень.\n' \
                           'Пример - ({y1|}+{y2|}-{y|Clay|W|}*{y3|}/2)*1.5'

    CurvesVarLog: Final = 'Выбирите чтобы добавить в выражение переменную'

    CurvesAddCalculatedCurve: Final = 'Добавить кривую Calculated Curve'

    CurvesAddRangeCurve: Final = 'Добавить кривую Range Curve'


def main_icon() -> str:
    return os.environ['project'] + '/InputData/resource/pictures/InputLogo.png'


class TitleName(Const):
    InputLogView: Final = 'InputLogs'
    ShapeEditWindow: Final = 'InputData'
    SplitEditWindow: Final = 'Split'
    ViewingLayersWindow: Final = 'Choose surface'
    SurfaceEditWindow: Final = 'Surface'


class ErrorMessage(Const):
    MinMaxValid: Final = 'Min should be less than max'
    EmptyName: Final = 'The name cannot be empty'
