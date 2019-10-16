import functools
import math

import numpy as np


class MedianAbsoluteDeviation(object):
    """
    Median Absolute Deviation
    """

    NMAD_CONSTANT = 1.4826

    STANDARD_DEVIATIONS = {
        1: 68.27,
        2: 95.45,
        3: 99.73
    }

    def __init__(self, data):
        self._data = data
        self._data_median = np.median(self.data, overwrite_input=True)

    @property
    def data(self):
        return self._data

    @property
    def data_median(self):
        return self._data_median

    def standard_deviation(self, width=1, absolute=False):
        return self.percentile(self.STANDARD_DEVIATIONS[width], absolute)

    def absolute_difference(self, a):
        return math.fabs(a - self.data_median)

    @functools.lru_cache(1)
    def normalized(self):
        """
        NMAD from Höhle & Höhle, 2009
        """
        absolute_difference = np.vectorize(self.absolute_difference)
        return self.NMAD_CONSTANT * np.median(absolute_difference(self.data))

    @functools.lru_cache(16)
    def percentile(self, percent, absolute=False):
        if absolute:
            data = np.abs(self.data)
        else:
            data = self.data

        return np.percentile(data, percent, overwrite_input=True)
