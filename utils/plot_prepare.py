from matplotlib.ticker import MultipleLocator, AutoMinorLocator


def plot_prepare(ax, base_scale):
    ax.set_xlim(0, base_scale)
    ax.set_ylim(0, base_scale)

    ax.xaxis.set_major_locator(MultipleLocator(base_scale / 5))
    ax.yaxis.set_major_locator(MultipleLocator(base_scale / 5))

    ax.xaxis.set_minor_locator(AutoMinorLocator(5))
    ax.yaxis.set_minor_locator(AutoMinorLocator(5))

    ax.grid(which='major', color='#CCCCCC', linestyle='--')
    ax.grid(which='minor', color='#CCCCCC', linestyle=':')