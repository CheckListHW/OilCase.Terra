def transform_data(data: []) -> dict:
    map_dict = {}
    for i in range(len(data)):
        map_dict[i] = {}
        for j in range(len(data[i])):
            start = False
            map_dict[i][j] = []
            for k in range(len(data[i][j])):
                if data[i][j][k] and not start:
                    start = True
                    map_dict[i][j].append({'s': k, 'e': len(data[i][j])-1})
                elif not data[i][j][k] and start:
                    start = False
                    map_dict[i][j][-1]['e'] = k - 1
            if not map_dict[i][j]:
                map_dict[i].pop(j)
        if map_dict[i] == {}:
            map_dict.pop(i)
    return map_dict


def dict_update(old: dict, new: dict) -> dict:
    if old and new:
        for i in set(list(old.keys()) + list(new.keys())):
            if old.get(i) is not None:
                if new.get(i) is not None:
                    if type(old[i]) in [list]:
                        old[i] += new[i]
                    else:
                        dict_update(old[i], new[i])
            else:
                old[i] = new[i]
        return old
    else:
        return new
