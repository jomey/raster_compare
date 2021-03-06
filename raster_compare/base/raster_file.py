import errno
import functools
import numpy as np
import os
from osgeo import gdal, gdalnumeric

from .median_absolute_deviation import MedianAbsoluteDeviation


class RasterFile(object):
    def __init__(self, filename, band_number):
        self.file = str(filename)
        self._band_number = band_number

        self._geotransform = None
        self._extent = None
        self._xy_meshgrid = None

        self._mad = None

        self._slope = None
        self._aspect = None

    @property
    def file(self):
        return self._file

    @file.setter
    def file(self, filename):
        if os.path.exists(filename):
            self._file = gdal.Open(filename)
        else:
            raise FileNotFoundError(
                errno.ENOENT, os.strerror(errno.ENOENT), filename
            )

    @property
    def band_number(self):
        return self._band_number

    @band_number.setter
    def band_number(self, band_number):
        self._band_number = band_number

    @property
    def mad(self):
        if self._mad is None:
            band_values = self.band_values()
            band_values = band_values[np.isfinite(band_values)].compressed()
            self._mad = MedianAbsoluteDeviation(band_values)
        return self._mad

    @property
    def geo_transform(self):
        if self._geotransform is None:
            self._geotransform = self.file.GetGeoTransform()
        return self._geotransform

    @property
    def x_top_left(self):
        return self.geo_transform[0]

    @property
    def y_top_left(self):
        return self.geo_transform[3]

    @property
    def x_resolution(self):
        return self.geo_transform[1]

    @property
    def y_resolution(self):
        return self.geo_transform[5]

    @property
    def extent(self):
        if self._extent is None:
            x_bottom_right = \
                self.x_top_left + self.file.RasterXSize * self.x_resolution
            y_bottom_right = \
                self.y_top_left + self.file.RasterYSize * self.y_resolution

            self._extent = (
                self.x_top_left, x_bottom_right,
                self.y_top_left, y_bottom_right
            )
        return self._extent

    @property
    def xy_meshgrid(self):
        """
        Upper Left coordinate for each cell

        :return: Numpy meshgrid
        """
        if self._xy_meshgrid is None:
            x_size = self.file.RasterXSize
            y_size = self.file.RasterYSize
            self._xy_meshgrid = np.meshgrid(
                np.arange(
                    self.x_top_left,
                    self.x_top_left + x_size * self.x_resolution,
                    self.x_resolution,
                    dtype=np.float32,
                ),
                np.arange(
                    self.y_top_left,
                    self.y_top_left + y_size * self.y_resolution,
                    self.y_resolution,
                    dtype=np.float32,
                )
            )
        return self._xy_meshgrid

    def band_values(self, **kwargs):
        """
        Method to read band from arguments or from initialized raster.
        Will mask values defined in the band NoDataValue and store this mask
        with the `current_mask` property if the band is the same as the
        initialized one.

        :param kwargs:
            'band_number': band_number to read instead of the one given with
                           the initialize call.

        :return: Numpy masked array
        """
        band_number = kwargs.get('band_number', self.band_number)

        band = self.file.GetRasterBand(band_number)
        values = np.ma.masked_values(
            gdalnumeric.BandReadAsArray(band),
            band.GetNoDataValue(),
            copy=False
        )

        del band
        return values

    def get_raster_attribute(self, attribute, **kwargs):
        raster = gdal.DEMProcessing(
            '', self.file, attribute, format='MEM', **kwargs
        )
        raster_band = raster.GetRasterBand(1)
        raster_values = np.ma.masked_values(
            gdalnumeric.BandReadAsArray(raster_band),
            raster_band.GetNoDataValue(),
            copy=False
        )

        del raster
        del raster_band

        return raster_values

    @functools.lru_cache(16)
    def hill_shade(self, **kwargs):
        return self.get_raster_attribute('hillshade', **kwargs)

    @property
    def slope(self):
        if self._slope is None:
            self._slope = self.get_raster_attribute('slope')
        return self._slope

    @property
    def aspect(self):
        if self._aspect is None:
            self._aspect = self.get_raster_attribute('aspect')
        return self._aspect

    def join_masks(self, attribute, other):
        """
        Extend the numpy mask for given attribute with mask from given other
        masked numpy array.

        Note: This will *permanently* change the mask.

        :param attribute: name of property to change the mask
        :param other: Masked numpy array to extend the mask with
        """
        attr = getattr(self, attribute)
        attr.mask = np.ma.mask_or(attr.mask, other.mask)
