import os
import sys

import matplotlib
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable


class PlotBase(object):
    SCALE_BAR_LABEL = {
        'Aspect': 'Degree',
        'Elevation': '∆h [m]',
        'Slope': 'Angle',
    }

    NUM_BINS = 50

    TITLE_FONT_SIZE = 20
    LABEL_FONT_SIZE = 16

    LIDAR_LABEL = 'Lidar'
    SFM_LABEL = 'SfM'

    DEFAULT_DPI = 200

    BOUNDING_BOX = dict(
        boxstyle='square',
        edgecolor='black',
        facecolor='grey',
        alpha=0.2,
        pad=0.6
    )

    def __init__(self, data, **kwargs):
        self._output_path = kwargs['output_path']
        if 'ortho_image' in kwargs:
            self._ortho_image = plt.imread(kwargs['ortho_image'])
        self.data = data
        self.configure_matplotlib()
        self.data_description = kwargs.get(
            'data_description', 'Elevation'
        )

    @property
    def data_description(self):
        return self._data_description

    @data_description.setter
    def data_description(self, value):
        self._data_description = value

    @staticmethod
    def configure_matplotlib():
        # Enable running on headless devices
        if sys.stdout.isatty():
            matplotlib.use('Agg')

        # Font sizes
        matplotlib.rcParams['axes.titlesize'] = PlotBase.TITLE_FONT_SIZE
        matplotlib.rcParams['axes.labelsize'] = PlotBase.LABEL_FONT_SIZE

        # Figure settings
        matplotlib.rcParams['figure.titlesize'] = PlotBase.TITLE_FONT_SIZE
        matplotlib.rcParams['figure.dpi'] = PlotBase.DEFAULT_DPI

        # Axes
        matplotlib.rcParams['axes.formatter.useoffset'] = False

        # Save settings
        matplotlib.rcParams['savefig.bbox'] = 'tight'

        # Save figure text editable
        matplotlib.rcParams['pdf.fonttype'] = 42
        matplotlib.rcParams['ps.fonttype'] = 42

    @property
    def output_path(self):
        return self._output_path

    @property
    def output_file(self):
        try:
            return os.path.join(self.output_path, self.OUTPUT_FILE_NAME)
        except NameError:
            print('*** OUTPUT_FILE_NAME not defined ***')
            print('*** Figure NOT saved ***')
            return

    @property
    def ortho_image(self):
        return self._ortho_image

    def __getattr__(self, name):
        return getattr(self.data, name)

    @staticmethod
    def text_box_args(x, y, text, **kwargs):
        return dict(
            x=x,
            y=y,
            s=text,
            ha='left', va='top', bbox=PlotBase.BOUNDING_BOX, **kwargs
        )

    def add_ortho_background(self, ax, raster):
        ax.imshow(self.ortho_image, zorder=0, extent=raster.extent)

    @staticmethod
    def add_hillshade_background(ax, raster_file):
        ax.imshow(
            raster_file.hill_shade,
            extent=raster_file.extent,
            cmap='gray', clim=(1, 255)
        )

    @staticmethod
    def add_to_legend(axes, text, **kwargs):
        text = mpatches.Patch(color='none', label=text)
        handles, labels = axes.get_legend_handles_labels()
        handles.append(text)
        axes.legend(handles=handles, prop={'family': 'monospace'}, **kwargs)

    @staticmethod
    def insert_colorbar(axes, data, label, **kwargs):
        """
        Insert color bar to given figure.
        If the kwargs contains the 'right' parameter, the method adjusts to a
        different logic for adding a color bar axes.

        :param axes: Axes to append to
        :param data: Data to plot the colorbar for
        :param label: Label for the colorbar
        :param kwargs: Any arguments a colorbar and it's label would accept
            For single axes, the 'pad' parameter can adjust spacing between
            For multiple axes, two parameters are **required**
                'right': percentage to adjust the figure for axes
                'rect': the dimensions for axes [left, bottom, width, height]
        :return: Inserted color bar
        """
        figure = axes.get_figure()
        if 'right' not in kwargs:
            legend = make_axes_locatable(axes)
            padding = kwargs.pop('pad', 0.1)
            cax = legend.append_axes("right", size="5%", pad=padding)
        else:
            figure.subplots_adjust(right=kwargs.pop('right'))
            cax = figure.add_axes(kwargs.pop('rect'))

        color_bar = figure.colorbar(data, cax=cax, **kwargs)
        color_bar.set_label(
            label=label,
            rotation=kwargs.pop('rotation', 270),
            labelpad=kwargs.pop('labelpad', 10)
        )
        return color_bar

    def print_status(self, message=''):
        status = 'Plotting ' + self.__class__.__name__

        if len(message) > 0:
            status += ':\n   ' + message + '\n'

        print(status)
