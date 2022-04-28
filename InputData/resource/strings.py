import os
from typing import Final

from InputData.resource.const_class import Const


class Tips(Const):
    SIMPLIFYBUTTON: Final = "Раставляет точки по периметру линии \n" \
                            "равно удаленно друг от друга"


def main_icon() -> str:
    return os.environ['project'] + '/InputData/resource/pictures/InputLogo.png'


class TitleName:
    RoofExportDialog: Final = 'Roof export'
    RoofProfileEditWindow: Final = 'Roof profile'
    ShapeEditWindow: Final = 'InputData'
    SplitEditWindow: Final = 'Split'
    ViewingLayersWindow: Final = 'Choose surface'
    SurfaceEditWindow: Final = 'Surface'
