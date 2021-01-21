import pandas as pd

from .source_files import DB_CONNECTION
from .source_files_extended import *

aso_snow_depth_values = load_aso_depth()
sfm_snow_free_values, sfm_snow_on_values, dem_values = load_elevations(aso_snow_depth_values.mask)

df = pd.DataFrame({
        'aso_snow_depth': aso_snow_depth_values.ravel(),
        'sfm_snow_depth': sfm_snow_depth_values.ravel(),
        'elevation': dem_values.ravel(),
        'slope': dem.slope.ravel(),
        'aspect': dem.aspect.ravel(),
        'sfm_point_count_snow_on': load_point_count(sfm_snow_on, aso_snow_depth_values.mask).ravel(),
        'point_spread_snow_on': elevation_spread(sfm_snow_on, aso_snow_depth_values.mask).ravel(),
        'sfm_point_count_snow_free': load_point_count(sfm_snow_free, aso_snow_depth_values.mask).ravel(),
        'point_spread_snow_free': elevation_spread(sfm_snow_free, aso_snow_depth_values.mask).ravel(),
        'casi_class': load_classifier_data(aso_snow_depth_values.mask).ravel(),
})

df.dropna(inplace=True, how='all', subset=['aso_snow_depth', 'sfm_snow_depth'])

df['sd_difference'] = df.sfm_snow_depth - df.aso_snow_depth

convert_to_int = ['slope', 'aspect',
                  'sfm_point_count_snow_on', 'sfm_point_count_snow_free',
                  'point_spread_snow_on', 'point_spread_snow_free']
for column in convert_to_int:
    df[column] = df[column].fillna(-1).astype('int16')


df.to_sql(
    'ERW_analysis',
    con=DB_CONNECTION,
    index=False,
    if_exists='replace',
    chunksize=100000
)
