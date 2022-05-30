import os


class MetaConst(type):
    def __setattr__(cls, name, value):
        pass


class Const(metaclass=MetaConst):
    pass


def main_icon() -> str:
    return os.environ['project'] + '/res/pictures/InputLogo.png'


special_logs_name = ['index|', 'HeightAboveFWL|', 'old_index|']
default_logs_name = ['SeismicTraces']


class Limits(Const):
    MAX_TREND_RATIO = 1
    MAX_HEIGHT = 500
    MIN_HEIGHT = 0
    WIDTH = 25
    LENGTH = 25
    BASE_PLOT_SCALE = 25


class TitleName:
    RoofExportDialog = 'Roof export'
    RoofProfileEditWindow = 'Roof profile'
    ShapeEditWindow = 'InputData'
    SplitEditWindow = 'Split'
    ViewingLayersWindow = 'Choose surface'
    SurfaceEditWindow = 'Surface'
    InputLogView = 'InputLogs'


class SelectionMessage:
    UpdateOrCreate = 'Вы хотитие добавить новую кривую или обновить старую'


class ErrorMessage(Const):
    MinMaxValid = 'Min should be less than max'
    EmptyName = 'The name cannot be empty'


class Tips(Const):
    SIMPLIFY_BUTTON = "Раставляет точки по периметру линии \n" \
                      "равно удаленно друг от друга"

    CreateWaterLog = "Нужно выбрать если кривая будет применяться к Водной части фации"

    CreateOilLog = "Нужно выбрать если кривая будет применяться к Нефтяной части фации"

    CreateLog = "Можно добавить два типа кривых:\n" \
                "Первый тип - задаеться минимумом и максимумом.\n" \
                "В нем точки для кривой будут генерироваться " \
                "рандомно в заданом диапазоне." \
                "\n\n" \
                "Второй тип - вычисляемая кривая она вычисляеться на основе кривой(кривых)" \
                " первого типа и заданного уравнения"

    CreateNameLog = 'Обозначение кривой состоит из имени,\n' \
                    'приндлежности к воде или нефти и приндлежности к фации'

    CreateCalcLog = 'В выражении можно использовать следующие знаки:' \
                    ' .,+,-.*./,(,),**. ** - степень.\n' \
                    'Пример - ({y1|}+{y2|}-{y|Clay|W|}*{y3|}/2)*1.5'

    CurvesVarLog = 'Выбирите чтобы добавить в выражение переменную'

    CurvesAddCalculatedCurve = 'Добавить кривую Calculated Curve'

    CurvesAddRangeCurve = 'Добавить кривую Range Curve'

    ChooseLayer = 'Изменить видимые слои'

    AddLogWindow = 'Создать кривые'

    CreateCoreSampleWindow = 'Добавить кривые имитирующие керн'

    CreateOWCWindow = 'Указать ВНК для фаций'

    AttachLogWindow = 'Связать кривые и фации'

    LogSelect = 'Изменить отображаемую кривую'
