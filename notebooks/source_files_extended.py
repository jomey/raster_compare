import numpy as np

from source_files import aso_snow_depth, sfm_snow_depth, SNOW_DEPTH_DIR
from raster_compare.base import RasterFile

# ** NOTE **
# All source files were masked to only ERW watershed boundaries.
##

###
# ASO data
###
aso_snow_depth_values = aso_snow_depth.band_values()
# Mask to all pixels, where ASO snow depth values are present
np.ma.masked_where(
    aso_snow_depth_values <= 0.0,
    aso_snow_depth_values,
    copy=False
)

###
# SfM data
###
assert aso_snow_depth.geo_transform == sfm_snow_depth.geo_transform

sfm_snow_depth_values = sfm_snow_depth.band_values()
np.ma.masked_where(
    aso_snow_depth_values.mask,
    sfm_snow_depth_values,
    copy=False
)

SFM_SNOW_FREE = SNOW_DEPTH_DIR / '20180912_Agisoft_ERW_basin_dsm_1m.tif'
SFM_SNOW_ON = SNOW_DEPTH_DIR / '20180524_Agisoft_ERW_basin_dsm_1m.tif'

sfm_snow_free = RasterFile(SFM_SNOW_FREE, band_number=3)
assert aso_snow_depth.geo_transform == sfm_snow_free.geo_transform

sfm_snow_on = RasterFile(SFM_SNOW_ON, band_number=3)
assert aso_snow_depth.geo_transform == sfm_snow_on.geo_transform

###
# Classification
###
casi_classifier = RasterFile(
    SNOW_DEPTH_DIR / '20180524_ASO_CASI_ERW_basin_1m.tif',
    band_number=1
)
assert aso_snow_depth.geo_transform == casi_classifier.geo_transform

casi_classification = casi_classifier.band_values()
np.ma.masked_where(
    aso_snow_depth_values.mask,
    casi_classification,
    copy=False
)

###
# Reference DEM
###
DEM_SNOW_FREE = SNOW_DEPTH_DIR / '20180912_ASO_ERW_basin_dsm_1m.tif'

dem = RasterFile(DEM_SNOW_FREE, band_number=1)
assert aso_snow_depth.geo_transform == dem.geo_transform

###
# Co-registration DEM
###
DEM_ASO_LIDAR_SNOW_ON = SNOW_DEPTH_DIR / '20180524_Lidar_ERW_basin_dsm_1m.tif'

dem_co_reg = RasterFile(DEM_ASO_LIDAR_SNOW_ON, band_number=3)
assert aso_snow_depth.geo_transform == dem_co_reg.geo_transform

STABLE_GROUND = SNOW_DEPTH_DIR / '20180524_NoR_FS_no_snow_1m.tif'


def load_elevations():
    sfm_snow_free_values = sfm_snow_free.band_values()
    sfm_snow_on_values = sfm_snow_on.band_values()
    dem_values = dem.band_values()

    for values in [
        sfm_snow_free_values,
        sfm_snow_on_values,
        dem_values
    ]:
        np.ma.masked_where(aso_snow_depth_values.mask, values, copy=False)

    return sfm_snow_free_values, sfm_snow_on_values, dem_values


def load_reference_dem():
    dem_values = dem.band_values()
    np.ma.masked_where(aso_snow_depth_values.mask, dem_values, copy=False)
    return dem_values


def load_hillshade():
    hillshade_snow_on = dem.hill_shade(**HILLSHADE_SNOW_ON)
    hillshade_snow_free = dem.hill_shade(**HILLSHADE_SNOW_FREE)
    return hillshade_snow_on, hillshade_snow_free


def load_point_count(raster):
    point_count = raster.band_values(band_number=4)
    np.ma.masked_where(aso_snow_depth_values.mask, point_count, copy=False)
    return point_count


def elevation_spread(raster):
    min_elevation = raster.band_values(band_number=1)
    np.ma.masked_where(aso_snow_depth_values.mask, min_elevation, copy=False)
    max_elevation = raster.band_values(band_number=2)
    np.ma.masked_where(aso_snow_depth_values.mask, max_elevation, copy=False)
    return max_elevation - min_elevation

