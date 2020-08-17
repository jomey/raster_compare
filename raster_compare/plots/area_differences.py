import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy as np
import statsmodels.api as sm
from matplotlib.gridspec import GridSpec
from palettable.colorbrewer.diverging import RdBu_5 as PlotColor

from .plot_base import PlotBase


# Plot differences between rasters and show histogram of the differences
class AreaDifferences(PlotBase):
    TITLE = '{0} differences'

    HIST_TEXT = 'Median (abs): {:4.2f}\n' \
                'NMAD        : {:4.2f}\n' \
                '68.3%  (abs): {:4.2f}\n' \
                '95%    (abs): {:4.2f}'
    HIST_BIN_WIDTH = 0.01
    BOX_PLOT_TEXT = '{0:8}: {1:6.3f}'
    BOX_PLOT_WHISKERS = [5, 95]

    OUTPUT_FILE_NAME = 'elevation_differences.png'

    COLORMAP = PlotColor.mpl_colormap

    def add_hist_stats(self, ax):
        box_text = self.HIST_TEXT.format(
            self.data.mad.percentile(50, absolute=True),
            self.data.mad.normalized(),
            self.data.mad.standard_deviation(1, absolute=True),
            self.data.mad.standard_deviation(2, absolute=True),
        )
        self.add_to_legend(
            ax, box_text,
            loc='upper left', handlelength=0, handletextpad=0,
        )

    def add_box_plot_stats(self, ax, box_plot_data, data):
        text = [
            self.BOX_PLOT_TEXT.format(
                'Median', box_plot_data['medians'][0].get_ydata()[0]
            ),
            self.BOX_PLOT_TEXT.format('Mean', data.mean()),
            self.BOX_PLOT_TEXT.format('Nmad', self.data.mad.normalized()),
            self.BOX_PLOT_TEXT.format('Std', data.std()),
        ]
        self.add_to_legend(
            ax, '\n'.join(text), handlelength=0, handletextpad=0
        )

    # TODO - Zoom into each graph to only show values within the 95th
    #  percentile
    def plot(self):
        self.print_status()

        figure = plt.figure(
            figsize=(17, 14),
            dpi=150,
            constrained_layout=False,
        )
        grid_opts = dict(figure=figure, height_ratios=[3, 1])

        difference = self.data.band_values

        if self.data_description == 'Elevation':
            grid_spec = GridSpec(
                nrows=2, ncols=3, width_ratios=[3, 2, 2], **grid_opts
            )
            bins = np.arange(
                difference.min(),
                difference.max() + self.HIST_BIN_WIDTH,
                self.HIST_BIN_WIDTH
            )
            bounds = dict(
                norm=colors.BoundaryNorm(
                    boundaries=bins, ncolors=self.COLORMAP.N,
                )
            )
        else:
            grid_spec = GridSpec(
                nrows=2, ncols=2, width_ratios=[3, 2], **grid_opts
            )
            bounds = dict()

        ax1 = figure.add_subplot(grid_spec[0, :])
        diff_plot = ax1.imshow(
            difference,
            cmap=self.COLORMAP,
            alpha=0.8,
            extent=self.sfm.extent,
            **bounds
        )
        ax1.set_title(self.TITLE.format(self.data_description))
        self.insert_colorbar(
            ax1, diff_plot, self.SCALE_BAR_LABEL[self.data_description]
        )

        difference = difference[np.isfinite(difference)].compressed()

        # Reset bins to entire range of values for Histogram
        bins = np.arange(
            np.nanmin(difference),
            np.nanmax(difference),
            self.HIST_BIN_WIDTH
        )

        ax2 = figure.add_subplot(grid_spec[1, 0])
        ax2.hist(difference, bins=bins)
        ax2.set_xlabel(self.SCALE_BAR_LABEL[self.data_description])
        ax2.set_ylabel("Count $(10^5)$")
        ax2.ticklabel_format(style='sci', axis='y', scilimits=(4, 4))
        ax2.yaxis.get_offset_text().set_visible(False)
        if self.data_description == 'Elevation':
            ax2.set_title('Relative Elevation Differences')

        ax3 = figure.add_subplot(grid_spec[1, 1])
        box = ax3.boxplot(
            difference,
            sym='k+',
            whis=self.BOX_PLOT_WHISKERS,
            positions=[0.1]
        )
        ax3.set_xlim([0, .35])
        ax3.tick_params(
            axis='x', which='both', bottom=False, top=False, labelbottom=False
        )
        ax3.set_ylabel(self.SCALE_BAR_LABEL[self.data_description])
        self.add_box_plot_stats(ax3, box, difference)
        if self.data_description == 'Elevation':
            ax3.set_title('Relative Elevation Differences')

        if self.data_description == 'Elevation':
            ax4 = figure.add_subplot(grid_spec[1, 2])
            probplot = sm.ProbPlot(difference)
            probplot.qqplot(ax=ax4, line='s')
            ax4.get_lines()[0].set(markersize=1)
            ax4.get_lines()[1].set(color='black', dashes=[4, 1])
            ax4.set_title('Normal Q-Q Plot')

        plt.savefig(self.output_file)
        return figure
