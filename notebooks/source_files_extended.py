import numpy as np

from source_files import SNOW_DEPTH_DIR, HILLSHADE_SNOW_FREE, HILLSHADE_SNOW_ON
from raster_compare.base import RasterFile

# ** NOTE **
# All source files were masked to only ERW watershed boundaries.
##

###
# ASO data
###
aso_snow_depth = RasterFile(
    SNOW_DEPTH_DIR / '20180524_ASO_snow_depth_1m.tif',
    band_number=1
)
def load_aso_depth():
    aso_snow_depth_values = aso_snow_depth.band_values()
    # Mask to all pixels, where ASO snow depth values are present
    np.ma.masked_where(
        aso_snow_depth_values <= 0.0,
        aso_snow_depth_values,
        copy=False
    )
    return aso_snow_depth_values

###
# SfM data
###
sfm_snow_depth = RasterFile(
    SNOW_DEPTH_DIR / '20180524_Agisoft_snow_depth_1m.tif',
    band_number=1
)
assert aso_snow_depth.geo_transform == sfm_snow_depth.geo_transform

def load_sfm_depth(aso_mask):
    sfm_snow_depth_values = sfm_snow_depth.band_values()
    np.ma.masked_where(
        aso_mask,
        sfm_snow_depth_values,
        copy=False
    )
    return sfm_snow_depth_values

SFM_SNOW_FREE = SNOW_DEPTH_DIR / '20180912_Agisoft_ERW_basin_dsm_1m.tif'
sfm_snow_free = RasterFile(SFM_SNOW_FREE, band_number=3)
assert aso_snow_depth.geo_transform == sfm_snow_free.geo_transform

SFM_SNOW_ON = SNOW_DEPTH_DIR / '20180524_Agisoft_ERW_basin_dsm_1m.tif'
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

def load_classifier_data(aso_mask):
    casi_classification = casi_classifier.band_values()
    np.ma.masked_where(
       aso_mask,
       casi_classification,
       copy=False
    )
    return casi_classification

###
# Reference DEM
###
DEM_SNOW_FREE = SNOW_DEPTH_DIR / '20180912_ASO_ERW_basin_dsm_1m.tif'
reference_dem = RasterFile(DEM_SNOW_FREE, band_number=1)
assert aso_snow_depth.geo_transform == reference_dem.geo_transform

###
# Co-registration DEM
###
DEM_ASO_LIDAR_SNOW_ON = SNOW_DEPTH_DIR / '20180524_Lidar_ERW_basin_dsm_1m.tif'
dem_co_reg = RasterFile(DEM_ASO_LIDAR_SNOW_ON, band_number=3)
assert aso_snow_depth.geo_transform == dem_co_reg.geo_transform

STABLE_GROUND = SNOW_DEPTH_DIR / '20180524_NoR_FS_no_snow_1m.tif'
control_surfaces = RasterFile(STABLE_GROUND, band_number=1)
assert aso_snow_depth.geo_transform == control_surfaces.geo_transform

###
# Hillshade
# From 3m DEM; using the 1m had too many artifacts
###
HS_SNOW_FREE = SNOW_DEPTH_DIR / '20180912_Lidar_hs_1m.tif'
hillshade_snow_free = RasterFile(HS_SNOW_FREE, band_number=1)
HS_SNOW_ON = SNOW_DEPTH_DIR / '20180524_Lidar_hs_1m.tif'
hillshade_snow_on = RasterFile(HS_SNOW_ON, band_number=1)

def load_control_surfaces():
    control_surfaces_values = control_surfaces.band_values()
    control_surfaces_values = np.ma.masked_where(
        control_surfaces_values == 0, 
        control_surfaces_values, 
        copy=False
    )
    
    return control_surfaces_values
    

def load_elevations(aso_mask):
    sfm_snow_free_values = sfm_snow_free.band_values()
    sfm_snow_on_values = sfm_snow_on.band_values()

    for values in [
        sfm_snow_free_values,
        sfm_snow_on_values,
    ]:
        np.ma.masked_where(aso_mask, values, copy=False)

    return sfm_snow_free_values, sfm_snow_on_values, load_reference_dem(aso_mask)


def load_reference_dem(aso_mask):
    return np.ma.masked_where(
        aso_mask, reference_dem.band_values(), copy=False
    )

def load_hillshade(aso_mask):
    snow_on = np.ma.masked_where(
        aso_mask, hillshade_snow_on.band_values(), copy=False
    )
    snow_free = np.ma.masked_where(
        aso_mask, hillshade_snow_free.band_values(), copy=False
    )
    return snow_on, snow_free


def load_point_count(raster, aso_mask):
    point_count = raster.band_values(band_number=4)
    np.ma.masked_where(aso_mask, point_count, copy=False)
    return point_count


def elevation_spread(raster, aso_mask):
    min_elevation = raster.band_values(band_number=1)
    np.ma.masked_where(aso_mask, min_elevation, copy=False)
    max_elevation = raster.band_values(band_number=2)
    np.ma.masked_where(aso_mask, max_elevation, copy=False)
    return max_elevation - min_elevation
