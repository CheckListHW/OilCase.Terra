class MetaConst(type):
    def __setattr__(cls, name, value):
        pass


class Const(metaclass=MetaConst):
    pass
