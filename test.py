from itertools import groupby

x = ['J', 'Pc', 'Poro_RHOB', 'Vsh', 'DeltaH', 'Poro_NPHI', 'Pc', 'Poro_RHOB_NPHI', 'Sw', 'Perm',
     'J', 'SwJ', 'J', 'Pc', 'Poro_RHOB', 'Vsh', 'DeltaH', 'Poro_NPHI', 'Pc', 'Poro_RHOB_NPHI', 'Sw', 'Perm',
     'J', 'SwJ'].__reversed__()
y = []
x = [y.append(i) for i in x if not y.__contains__(i)]
print(list(y.__reversed__()))
