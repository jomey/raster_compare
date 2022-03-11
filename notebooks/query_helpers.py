import math

import numba
import numpy as np
from numba import prange


def get_positive(data_frame, column_name):
    """
    Query given data frame for positive values, including zero

    :param data_frame: Pandas data frame to query
    :param column_name: column name to filter values by
    :return: DataFrame view
    """
    return data_frame.query(f'{column_name} >= 0')


def get_negative(data_frame, column_name):
    """
    Query given data frame for negative values, including null or NaN.

    From StackOverflow: Utilize the fact that np.nan != np.nan

    :param data_frame: Pandas data frame to query
    :param column_name: column name to filter values by
    :return: DataFrame view
    """
    return data_frame.query(
        f'({column_name} < 0) or ({column_name} != {column_name})'
    )


def get_no_data(data_frame, column_name):
    """
    Query given data frame for null or NaN.

    :param data_frame: Pandas data frame to query
    :param column_name: column name to filter values by
    :return: DataFrame view
    """
    return data_frame.query(f'{column_name} != {column_name}')


@numba.jit
def column_to_volume(snow_depth, x_resolution, y_resolution):
    length = len(snow_depth)
    resolution = math.fabs(x_resolution * y_resolution)
    result = np.zeros(length, dtype=snow_depth.dtype)
    for i in prange(length):
        result[i] = snow_volume(snow_depth[i], resolution)
    return result


@numba.jit
def snow_volume(snow_depth, resolution):
    if snow_depth < 0:
        return 0.0
    else:
        return resolution * snow_depth


@numba.jit
def column_to_swe(snow_depth, x_resolution, y_resolution):
    length = len(snow_depth)
    cell_area = math.fabs(x_resolution * y_resolution)
    result = np.zeros(length, dtype=snow_depth.dtype)
    for i in range(length):
        result[i] = swe_from_depth(snow_depth[i], cell_area)
    return result


@numba.jit
def swe_from_depth(snow_depth, cell_area):
    """
    Median SWE from ASO NSIDC map 394 kg/m^3
    SWE is returned as m^3
    """
    if snow_depth < 0:
        return 0.0
    else:
        return snow_depth * .394 * cell_area


def diff_vol_swe(df, aso, sfm):
    """
    Calculate snow depth differences, volume, and SWE for the
    given dataframe
    """
    df['sd_difference'] = df.sfm_snow_depth - df.aso_snow_depth
    df['aso_snow_volume'] = column_to_volume(
        df.aso_snow_depth.to_numpy(),
        aso.x_resolution,
        aso.y_resolution
    )
    df['sfm_snow_volume'] = column_to_volume(
        df.sfm_snow_depth.to_numpy(),
        sfm.x_resolution,
        sfm.y_resolution
    )
    df['aso_swe'] = column_to_swe(
        df.aso_snow_depth.to_numpy(),
        aso.x_resolution,
        aso.y_resolution
    )
    df['sfm_swe'] = column_to_swe(
        df.sfm_snow_depth.to_numpy(),
        sfm.x_resolution,
        sfm.y_resolution
    )
    return df
