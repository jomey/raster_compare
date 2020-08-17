import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm

from base.raster_file import RasterFile


def render_3d(source):
    x, y = source.xy_meshgrid

    fig, ax = plt.subplots(subplot_kw={'projection': '3d'})

    surface = ax.plot_surface(
        x, y, source.band_values().filled(np.nan),
        cmap=cm.get_cmap('jet'),
        linewidth=0,
        vmin=source.band_values().min(),
        vmax=source.band_values().max(),
        alpha=0.7,
    )

    ax.view_init(20, 20)
    fig.colorbar(surface)

    plt.show()


if __name__ == '__main__':
    lidar = RasterFile('', 1)
    render_3d(lidar)
