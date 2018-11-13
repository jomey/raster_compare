import argparse

from area_differences import AreaDifferences
from area_plot import AreaPlot
from base.raster_compare import RasterCompare
from histograms import Histogram
from regression import Regression
from ortho_difference import OrthoDifference

parser = argparse.ArgumentParser()
parser.add_argument(
    '--base-path',
    type=str,
    help='Root directory',
    required=True
)
parser.add_argument(
    '--lidar-dem',
    type=str,
    help='Relative path to lidar DEM relative from base path',
    required=True
)
parser.add_argument(
    '--sfm-dem',
    type=str,
    help='Relative path to SfM DEM relative from base path',
    required=True
)
parser.add_argument(
    '--shape-file',
    type=str,
    help='Shapefile for sfm and lidar relative from base path',
)
parser.add_argument(
    '--ortho-image',
    type=str,
    help='Path to ortho photo used as background in plots',
    required=True
)
parser.add_argument(
    '--output-path',
    type=str,
    help='Directory where plots should be saved to',
    default='comparison'
)
parser.add_argument(
    '--area-plots',
    action='store_true',
    help='Side by side comparison plots for elevation, slope, and aspect'
)
parser.add_argument(
    '--differences',
    action='store_true',
    help='Plots for elevation, slope, and aspect differences'
)
parser.add_argument(
    '--save-difference',
    action='store_true',
    help='Store the elevation difference in GeoTiff file'
)
parser.add_argument(
    '--histograms',
    action='store_true',
    help='Create histograms for elevation, slope, and aspect'
)
parser.add_argument(
    '--regression',
    action='store_true',
    help='Run regression analysis'
)

if __name__ == '__main__':
    arguments = parser.parse_args()

    comparison = RasterCompare(**vars(arguments))
    comparison.prepare()

    if arguments.area_plots:
        area_plot = AreaPlot(**comparison.file_args())
        [area_plot.plot(attr) for attr in AreaPlot.TYPES]
        del area_plot

    if arguments.differences:
        area_difference = AreaDifferences(**comparison.file_args())
        [area_difference.plot(attr) for attr in AreaDifferences.TYPES]
        if arguments.save_difference:
            area_difference.raster_difference.save()
        del area_difference

        ortho_difference = OrthoDifference(
            ortho_image=comparison.check_path(arguments.ortho_image),
            **comparison.file_args()
        )
        ortho_difference.plot()
        del ortho_difference

    if arguments.histograms:
        histogram = Histogram(**comparison.file_args())
        [histogram.plot(attr) for attr in Histogram.TYPES]
        del histogram

    if arguments.regression:
        regression = Regression(**comparison.file_args())
        regression.run()
