import functools

import numpy as np
import numba

from scipy.stats import norm


class MedianAbsoluteDeviation(object):
    """
    Median Absolute Deviation
    """

    NMAD_CONSTANT = 1.4826

    STANDARD_DEVIATIONS = {
        1: (1 - 2 * norm.cdf(-1)) * 100,
        2: (1 - 2 * norm.cdf(-2)) * 100,
        3: (1 - 2 * norm.cdf(-3)) * 100,
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

    @staticmethod
    @numba.jit(nopython=True, parallel=True)
    def absolute_difference(a, median):
        return np.fabs(a - median)

    @functools.lru_cache(1)
    def normalized(self):
        """
        NMAD from Höhle & Höhle, 2009
          NMAD = 1.4826 · median_j(|􏰀h_j − m􏰀_h |)
        """
        absolute_difference = self.absolute_difference(
            self.data, self.data_median
        )
        return self.NMAD_CONSTANT * np.median(absolute_difference)

    @functools.lru_cache(16)
    def percentile(self, percent, absolute=False):
        if absolute:
            data = np.abs(self.data)
        else:
            data = self.data

        return np.percentile(data, percent, overwrite_input=True)
