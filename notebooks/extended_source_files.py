# Additional resources for analysis
# Base files are declared in source_files.py

from source_files import *

HILLSHADE_SNOW_ON = dict(azimuth=100, altitude=47)
HILLSHADE_SNOW_FREE = dict(azimuth=247, altitude=32)

sfm_snow_free = RasterFile(SFM_SNOW_FREE, band_number=1)
sfm_snow_free_values = sfm_snow_free.band_values()

sfm_snow_on = RasterFile(SFM_SNOW_ON, band_number=1)
sfm_snow_on_values = sfm_snow_on.band_values()

sd_difference_values = sfm_snow_depth_values - aso_snow_depth_values

dem = RasterFile(DEM_SNOW_FREE, band_number=1)
dem_values = dem.band_values()

hillshade_snow_on = dem.hill_shade(**HILLSHADE_SNOW_ON)
hillshade_snow_free = dem.hill_shade(**HILLSHADE_SNOW_FREE)

for values in [sfm_snow_free_values, sfm_snow_on_values,
               sd_difference_values, dem_values]:
    np.ma.masked_where(aso_snow_depth_values.mask, values, copy=False)

assert aso_snow_depth.geo_transform == dem.geo_transform
assert aso_snow_depth.geo_transform == \
       sfm_snow_free.geo_transform == \
       sfm_snow_on.geo_transform
