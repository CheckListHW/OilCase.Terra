from typing import Any


def recursive_extraction(obj: [Any]) -> Any:
    if type(obj) in [str]:
        return obj
    elif type(obj) is dict:
        d = {}
        for val, key in zip(obj.values(), obj.keys()):
            d[key] = recursive_extraction(val)
        return d
    try:
        obj_list = iter(obj)
        return [recursive_extraction(i) for i in obj_list]
    except TypeError:
        if hasattr(obj, 'get_as_dict'):
            return obj.get_as_dict()
        else:
            if type(obj) in [float]:
                return round(obj, 5)
            return obj
