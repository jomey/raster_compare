import numpy as np

from .raster_file import RasterFile


class PixelClassifier(object):
    SNOW = 1
    VEGETATION = 2
    ROCK = 3
    CLOUD = 5

    def __init__(self, casi_file, cloud_file, return_diff_file=None):
        casi_mask = RasterFile(casi_file, band_number=1)
        self._data = casi_mask.band_values()

        cloud_mask = RasterFile(cloud_file, band_number=1)
        cloud_mask = cloud_mask.band_values()
        cloud_mask = np.ma.masked_where(
            cloud_mask == self.CLOUD, cloud_mask
        ).mask

        if return_diff_file is not None:
            return_diff_mask = RasterFile(return_diff_file, band_number=1)
            return_diff_mask = return_diff_mask.band_values()
            return_diff_mask = np.ma.masked_where(
                ((return_diff_mask < -0.1) | (return_diff_mask > .1)),
                return_diff_mask
            ).mask
            self._data[return_diff_mask] = self.VEGETATION

            del return_diff_mask

        self._data[cloud_mask] = self.CLOUD

        del cloud_mask

    def mask_to(self, casi_type, no_data_mask):
        return no_data_mask + \
               np.ma.masked_where(self._data != casi_type, self._data).mask

    def stable_surfaces(self, no_data_mask):
        return self.mask_to(self.ROCK, no_data_mask)

    def snow_surfaces(self, no_data_mask):
        return self.mask_to(self.SNOW, no_data_mask)
