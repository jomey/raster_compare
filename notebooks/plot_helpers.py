import matplotlib
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy as np
from matplotlib_scalebar.scalebar import ScaleBar
from palettable.colorbrewer.diverging import RdBu_5 as PlotColor

from raster_compare.plots import PlotBase

matplotlib.rcParams['axes.titlesize'] = 14
matplotlib.rcParams['axes.labelsize'] = 14
matplotlib.rcParams['legend.fontsize'] = 14
matplotlib.rcParams['figure.titlesize'] = 16
matplotlib.rcParams['figure.facecolor'] = 'f0f0f0'
matplotlib.rcParams['figure.subplot.wspace'] = 0.05
matplotlib.rcParams['figure.subplot.top'] = 0.92

COLORMAP = PlotColor.mpl_colormap
BOX_PLOT_TEXT = '{0:8}: {1:6.3f}'
LEGEND_TEXT = "{0:8}: {1:7.2f}"

ELEVATION_LABEL = 'Elevation (m)'
SNOW_DEPTH_LABEL = 'Snow Depth (m)'


def side_by_side_plot(difference, extent, ortho_image, hillshade=None):
    bin_steps = 5 * 0.01
    bins = np.arange(-1.50, 1.50 + bin_steps, step=bin_steps)
    bounds = dict(
        norm=colors.BoundaryNorm(boundaries=bins, ncolors=COLORMAP.N)
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
        cmap=COLORMAP,
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

    figure = plt.figure(figsize=(6, 6), constrained_layout=False)
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
            'Median', box_plot['medians'][0].get_ydata()[0]
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


def add_to_histogram(ax, data, label='', color='dodgerblue'):
    data = data[np.isfinite(data)].compressed()
    data_min = np.nanmin(data)
    data_max = np.nanmax(data)
    data_mean = np.nanmean(data)

    bins = np.arange(
        min(0., float(data_min)),
        data_max + .01,
        .01
    )

    ax.hist(data, bins=bins, color=color, label=label, alpha=0.8)
    ax.axvline(x=data_mean, color='darkorange', linewidth=2)
    # ax.annotate(label, (data_mean + .05, 10e4))

    return data, data_mean


def plot_histogram(data, tick_range, **kwargs):
    figure = plt.figure(**kwargs)
    ax = figure.add_subplot(111)

    text = []

    for dataset in data:
        values, data_mean = add_to_histogram(
            ax, dataset['data'], dataset['label'], dataset['color']
        )
        if len(data) > 1:
            text.append(dataset['label'])
        text.append("\n".join([
            LEGEND_TEXT.format(" Mean", data_mean),
            LEGEND_TEXT.format(" Median", np.nanmedian(values)),
            LEGEND_TEXT.format(" Std", np.nanstd(values)),
            "{0:8}: {1}".format(" Count", values.size),
        ]))

    ax.ticklabel_format(style='sci', axis='y', scilimits=(4, 4))
    ax.set_xlabel(SNOW_DEPTH_LABEL)
    ax.set_ylabel("Count $(10^4)$")
    ax.yaxis.get_offset_text().set_visible(False)
    ax.axvline(x=0, color='black', linewidth=2)
    ax.set_xlim(tick_range[0], tick_range[1])
    ax.set_xticks(np.arange(tick_range[0], tick_range[1] + 1))

    text = "\n".join(text)
    PlotBase.add_to_legend(
        ax,
        text,
        loc='center left',
        bbox_to_anchor=(1, 0.5),
    )

    return ax
