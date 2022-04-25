import pandas as pd


def prepare_array(layers: []) -> []:
    try:
        center = sum(layers[-1]) / len(layers[-1])
    except ZeroDivisionError:
        raise (ZeroDivisionError, prepare_array)

    layers.append([center for _ in layers[0]])
    center = sum(layers[0]) / len(layers[0])
    layers.insert(0, [center for _ in layers[0]])

    x = pd.DataFrame(layers)
    x = pd.DataFrame([x[i] for i in range(len(x.columns))])
    return x.values.tolist()


def data_for_plot_3d(layers_x: [], layers_y: [], layers_z: []):
    return prepare_array(layers_x), prepare_array(layers_y), prepare_array(layers_z)
