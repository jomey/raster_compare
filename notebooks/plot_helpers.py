import matplotlib
import matplotlib.colors as colors
import matplotlib.lines as mlines
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager

import numpy as np

from matplotlib.gridspec import GridSpec
from matplotlib_scalebar.scalebar import ScaleBar
from matplotlib.ticker import MultipleLocator

from palettable.scientific.sequential import LaJolla_20 as Hist2dColor
from palettable.colorbrewer.diverging import RdBu_5 as RedBlueCmap
from palettable.colorbrewer.sequential import Blues_9 as BlueCmap

from contextlib import contextmanager

from raster_compare.plots import PlotBase

LABEL_SIZE = 11

matplotlib.rcParams['axes.titlesize'] = LABEL_SIZE + 1
matplotlib.rcParams['axes.labelsize'] = LABEL_SIZE
matplotlib.rcParams['xtick.labelsize'] = LABEL_SIZE - 1
matplotlib.rcParams['ytick.labelsize'] = LABEL_SIZE - 1
matplotlib.rcParams['legend.fontsize'] = LABEL_SIZE + 1
matplotlib.rcParams['figure.titlesize'] = 16
matplotlib.rcParams['figure.facecolor'] = 'ffffff'
matplotlib.rcParams['figure.subplot.wspace'] = 0.05
matplotlib.rcParams['figure.subplot.top'] = 0.875
matplotlib.rcParams['figure.dpi'] = 300

HIST_2D_CMAP = Hist2dColor.mpl_colormap
RED_BLUE_CMAP = RedBlueCmap.mpl_colormap
BLUE_CMAP = BlueCmap.mpl_colormap

BOX_PLOT_TEXT = '{0:8}: {1:6.2f} {2}'
LEGEND_TEXT = "{0:8}: {1:7.2f} {2}"

ELEVATION_LABEL = 'Elevation (m)'
SNOW_DEPTH_LABEL = 'Snow Depth (m)'


def side_by_side_plot(difference, extent, ortho_image, hillshade=None):
    bin_steps = 5 * 0.01
    bins = np.arange(-1.50, 1.50 + bin_steps, step=bin_steps)
    bounds = dict(
        norm=colors.BoundaryNorm(boundaries=bins, ncolors=RED_BLUE_CMAP.N)
    )

    figure = plt.figure(
        figsize=(12, 14),
        dpi=150,
        constrained_layout=False,
    )

    ortho_image_gs = figure.add_gridspec(
        figure=figure, nrows=1, ncols=1, left=.54, right=.96,
    )
    grid_spec = figure.add_gridspec(
        figure=figure, nrows=1, ncols=1, left=.03, right=.46
    )

    ax1 = figure.add_subplot(grid_spec[:, :])
    if hillshade is not None:
        ax1.imshow(hillshade,
                   cmap='gray', clim=(1, 255),
                   alpha=0.3,
                   extent=extent)

    diff_plot = ax1.imshow(
        difference,
        cmap=RED_BLUE_CMAP,
        extent=extent,
        **bounds
    )
    cbar = PlotBase.insert_colorbar(
        ax1, diff_plot,
        SNOW_DEPTH_LABEL,
        ticks=[-1.5, -1, -0.5, 0, 0.5, 1, 1.5],
    )
    cbar.ax.set_yticklabels(
        ['< -1.5', '-1', '-0.5', '0', '0.5', '1', '> 1.5'],
    )

    ax_o = figure.add_subplot(ortho_image_gs[:, :])
    ax_o.set_yticklabels([])
    ax_o.set_xticklabels([])
    ax_o.imshow(plt.imread(ortho_image), extent=extent)

    return figure


def rotate_axis_labels(ax):
    ax.xaxis.set_ticks_position('both')
    ax.xaxis.set_tick_params(rotation=55)

    ax.yaxis.set_ticks_position('both')
    ax.yaxis.set_tick_params(rotation=55)

    ax.ticklabel_format(axis='both', style='plain')


def style_area_axes(axes):
    set_axes_style(axes[0])
    set_axes_style(axes[2])
    axes[0].set_xticks([])
    axes[0].set_yticks([])
    axes[2].set_xticks([])
    axes[2].set_yticks([])

    axes[0].add_artist(
        ScaleBar(1.0, location='lower left')
    )


def set_axes_style(axes):
    for axis in ['top', 'bottom', 'left', 'right']:
        axes.spines[axis].set_linewidth(1)
        axes.spines[axis].set_edgecolor('black')
    axes.patch.set_color('lightgrey')
    axes.patch.set_alpha(.5)


def make_box_plot(data, label):
    data = data[np.isfinite(data)].compressed()

    figure = plt.figure(figsize=(8, 5), constrained_layout=False)
    ax = figure.add_subplot(111)

    box_plot = plt.boxplot(
        data,
        widths=0.3,
        showfliers=False,
        labels=[label],
    )
    plt.setp(box_plot['boxes'], color='mediumblue', alpha=0.7, linewidth=1.5)
    plt.setp(box_plot['caps'], color='mediumblue', linewidth=1.5)
    plt.setp(
        box_plot['fliers'],
        markeredgecolor='dimgray',
        markersize=2.5,
        marker='+'
    )

    text = [
        BOX_PLOT_TEXT.format(
            'Median', box_plot['medians'][0].get_ydata()[0], 'm'
        ),
    ]
    PlotBase.add_to_legend(
        ax,
        '\n'.join(text),
        handlelength=0,
        handletextpad=0,
        loc='upper left',
        bbox_to_anchor=(1, 0.5),
    )

    return ax


class Histogram(object):
    MEAN_LINE_STYLE = dict(linestyle='dashed', color='dimgrey')

    @classmethod
    def add_to_plot(cls, ax, **dataset):
        data = dataset.pop('data')
        data = data[np.isfinite(data)].compressed()
        data_min = np.nanmin(data)
        data_max = np.nanmax(data)
        data_mean = np.nanmean(data)

        bins = np.arange(
            min(0., float(data_min)),
            data_max + .01,
            .01
        )

        color = dataset.pop('color', 'dodgerblue')
        ax.hist(
            data,
            bins=bins,
            label=dataset.pop('label', ''),
            histtype='stepfilled',
            color=color,
            alpha=dataset.pop('alpha', 0.6),
            ec='k',
        )

        if 'skip_mean' not in dataset:
            ax.axvline(x=data_mean, linewidth=2, **cls.MEAN_LINE_STYLE)

        return data, data_mean

    @classmethod
    @contextmanager
    def plot(cls, dataset, tick_range, **kwargs):
        figure = plt.figure(**kwargs)
        ax = figure.add_subplot(111)

        text = []
        has_mean = True

        for data in dataset:
            values, data_mean = cls.add_to_plot(ax, **data)

            if 'skip_mean' in data:
                has_mean = False

            if len(dataset) > 1 and 'label' in data:
                text.append(data['label'])

            text.append(LEGEND_TEXT.format(" Mean", data_mean, 'm'))
            text.append(LEGEND_TEXT.format(" Std", np.nanstd(values), 'm'))
            text.append(LEGEND_TEXT.format(
                "Median", np.nanmedian(values), 'm')
            )
            if 'legend' in data:
                text.append(data['legend'])

        ax.set_xlabel(SNOW_DEPTH_LABEL)
        PlotBase.format_axes_scientific(
            ax, 'y', (4, 4), rotation=90, labelpad=2, fontsize=LABEL_SIZE
        )
        ax.axvline(x=0, color='black', linewidth=2)
        ax.set_xlim(tick_range[0], tick_range[1])
        ax.set_xticks(np.arange(tick_range[0], tick_range[1] + 1))

        handles = dict(
            loc='center left',
            bbox_to_anchor=(1, 0.5),
        )

        if has_mean:
            handles['handles'] = mlines.Line2D(
                [], [], label='Mean', **cls.MEAN_LINE_STYLE
            )

        PlotBase.add_to_legend(
            ax, "\n".join(text), **handles,
            prop=font_manager.FontProperties(
                family='monospace',
                size=LABEL_SIZE - 1,
            )
        )

        yield ax

        return ax

