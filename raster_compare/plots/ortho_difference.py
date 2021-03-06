import matplotlib as mpl
import matplotlib.colors as colors
import matplotlib.pyplot as plt

from .plot_base import PlotBase
from .plot_layout import PlotLayout


class OrthoDifference(PlotBase):
    COLOR_MAP = ['dodgerblue', 'cyan', 'yellow', 'orange']
    COLOR_OVER = 'darkred'
    COLOR_UNDER = 'darkblue'

    OUTPUT_FILE_NAME = 'elevation_difference_overlay.png'

    def __init__(self, data, **kwargs):
        super().__init__(data, **kwargs)
        self._cmap = self.setup_color_map()
        self._bounds = self.set_bounds()

    @property
    def cmap(self):
        return self._cmap

    @property
    def bounds(self):
        return self._bounds

    def setup_color_map(self):
        cmap = mpl.colors.ListedColormap(self.COLOR_MAP)
        cmap.set_over(self.COLOR_OVER)
        cmap.set_under(self.COLOR_UNDER)
        return cmap

    def set_bounds(self):
        return [
            self.band_unfiltered.min(),
            self.mad.data_median - self.mad.standard_deviation(2),
            self.mad.data_median - self.mad.standard_deviation(1),
            self.mad.data_median,
            self.mad.data_median + self.mad.standard_deviation(1),
            self.mad.data_median + self.mad.standard_deviation(2),
            self.band_unfiltered.max()
        ]

    def plot(self):
        self.print_status()

        norm = mpl.colors.BoundaryNorm(self.bounds[1:-1], self.cmap.N)

        fig, (ax1, ax2, cax) = PlotLayout.two_row()

        diff_options = dict(
            extent=self.lidar.extent,
            zorder=1, norm=norm, cmap=self.cmap, alpha=0.5,
        )

        self.add_ortho_background(ax1, self.lidar)
        ax1.imshow(self.band_filtered, **diff_options)
        ax1.set_title('95th percentile', size=self.TITLE_FONT_SIZE)

        self.add_ortho_background(ax2, self.lidar)
        img = ax2.imshow(self.band_outliers, **diff_options)
        ax2.set_title('Outliers', size=self.TITLE_FONT_SIZE)

        fig.colorbar(
            img, cax=cax, orientation='horizontal', extend='both',
            extendfrac='auto', spacing='uniform', boundaries=self.bounds
        )

        plt.savefig(self.output_file)
