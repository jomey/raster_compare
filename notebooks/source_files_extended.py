import numpy as np
import os

from pathlib import PurePath

from raster_compare.base import RasterFile

# ** NOTE **
# All source files were masked to only ERW watershed boundaries.
##

HOME_DIR = PurePath(f"{os.environ['HOME']}/skiles-group1/ERW-SfM")
RESOLUTION='3m'
SNOW_DEPTH_DIR = HOME_DIR / RESOLUTION

###
# ASO data
###
aso_snow_depth = RasterFile(
    SNOW_DEPTH_DIR / f'20180524_ASO_snow_depth_{RESOLUTION}.tif',
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
    SNOW_DEPTH_DIR / f'20180524_Agisoft_snow_depth_{RESOLUTION}.tif',
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


sfm_snow_free = RasterFile(
    SNOW_DEPTH_DIR / f'20180912_Agisoft_ERW_basin_dsm_{RESOLUTION}.tif',
    band_number=1
)
assert sfm_snow_free.geo_transform == sfm_snow_depth.geo_transform

sfm_snow_on = RasterFile(
    SNOW_DEPTH_DIR / f'20180524_Agisoft_ERW_basin_dsm_{RESOLUTION}.tif',
    band_number=1
)
assert sfm_snow_on.geo_transform == sfm_snow_depth.geo_transform

###
# Classification
###
def load_classifier_data(aso_mask):
    casi_classifier = RasterFile(
        SNOW_DEPTH_DIR / f'20180524_ASO_CASI_ERW_basin_{RESOLUTION}.tif',
        band_number=1
    )
    assert aso_snow_depth.geo_transform == casi_classifier.geo_transform

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
def load_reference_dem(aso_mask):
    DEM_SNOW_FREE = SNOW_DEPTH_DIR / f'20180912_ASO_NSIDC_ERW_basin_dsm_{RESOLUTION}.tif'
    reference_dem = RasterFile(DEM_SNOW_FREE, band_number=1)
    assert aso_snow_depth.geo_transform == reference_dem.geo_transform

    return reference_dem, np.ma.masked_where(
        aso_mask, reference_dem.band_values(), copy=False
    )


###
# Co-registration DEM
###
def load_co_reg_dem():
    DEM_ASO_LIDAR_SNOW_ON = SNOW_DEPTH_DIR / f'20180524_Lidar_ERW_basin_dsm_{RESOLUTION}.tif'
    dem_co_reg = RasterFile(DEM_ASO_LIDAR_SNOW_ON, band_number=3)
    assert aso_snow_depth.geo_transform == dem_co_reg.geo_transform

    return dem_co_reg.band_values()


###
# Classification raster with control surfaces set to 1
###
def load_control_surfaces():
    STABLE_GROUND = SNOW_DEPTH_DIR / f'20180524_NoR_FS_no_snow_{RESOLUTION}.tif'
    control_surfaces = RasterFile(STABLE_GROUND, band_number=1)
    assert aso_snow_depth.geo_transform == control_surfaces.geo_transform

    control_surfaces_values = control_surfaces.band_values()
    control_surfaces_values = np.ma.masked_where(
        control_surfaces_values == 0,
        control_surfaces_values,
        copy=False
    )

    return control_surfaces_values


###
# Hillshade
###
def load_hillshade(aso_mask=None):
    hillshade = RasterFile(
        HOME_DIR / f'hillshade/20180912_Lidar_hs_ERW_basin_{RESOLUTION}.tif', 
        band_number=1
    )
    
    hillshade_values = hillshade.band_values()
    
    if aso_mask is not None:
        hillshade_values = np.ma.masked_where(
            aso_mask, hillshade_values, copy=False
        )
    
    return hillshade_values


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
