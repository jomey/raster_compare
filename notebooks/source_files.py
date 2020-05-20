from pathlib import PurePath

import numpy as np

from raster_compare.base import RasterFile

HOME_DIR = PurePath('/Volumes/warehouse/projects/UofU/ASO/ERW')

SNOW_DEPTH_DIR = HOME_DIR / 'snow-depth/3m'

ORTHO_IMAGE = HOME_DIR / 'Orthomosaic/ERW_20180524_Agisoft_rgb_5m_ortho.tif'
DEM_SNOW_FREE = SNOW_DEPTH_DIR / '20180912_QS_ERW_basin_dsm_3m.tif'

# ** NOTE **
# All source files were masked to only ERW watershed boundaries.
# See source_files_extended.py for additional analytical resources.
##

###
# ASO data
###
aso_snow_depth = RasterFile(
    SNOW_DEPTH_DIR / '20180524_ASO_snow_depth_3m.tif',
    band_number=1
)
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
sfm_snow_depth = RasterFile(
    SNOW_DEPTH_DIR / '20180524_Agisoft_snow_depth_3m.tif',
    band_number=1
)
assert aso_snow_depth.geo_transform == sfm_snow_depth.geo_transform

sfm_snow_depth_values = sfm_snow_depth.band_values()
np.ma.masked_where(
    aso_snow_depth_values.mask,
    sfm_snow_depth_values,
    copy=False
)

SFM_SNOW_FREE = SNOW_DEPTH_DIR / '20180912_Agisoft_ERW_basin_dsm_3m.tif'
SFM_SNOW_ON = SNOW_DEPTH_DIR / '20180524_Agisoft_ERW_basin_dsm_3m.tif'

###
# Classification
###

SNOW = 1.
VEGETATION = 2.
ROCK = 3.
WATER = 4.

CASI_MAPPING = [0., 1., 2., 3., np.inf]
CASI_CLASSES = ['Snow', 'Vegetation', 'Rock', 'Water']

casi_classifier = RasterFile(
    SNOW_DEPTH_DIR / '20180524_ASO_CASI_ERW_basin_3m.tif',
    band_number=1
)
casi_classification = casi_classifier.band_values()

assert aso_snow_depth.geo_transform == casi_classifier.geo_transform

np.ma.masked_where(
    aso_snow_depth_values.mask,
    casi_classification,
    copy=False
)

STABLE_GROUND = SNOW_DEPTH_DIR / 'ERW_20180524_NoR_FS_no_snow_3m.tif'
