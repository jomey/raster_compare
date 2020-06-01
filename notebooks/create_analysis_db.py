import pandas as pd

from source_files_extended import *

sfm_snow_free_values, sfm_snow_on_values, dem_values = load_elevations()

df = pd.DataFrame({
        'aso_snow_depth': aso_snow_depth_values.ravel(),
        'sfm_snow_depth': sfm_snow_depth_values.ravel(),
        'elevation': dem_values.ravel(),
        'slope': dem.slope.ravel(),
        'aspect': dem.aspect.ravel(),
        'sfm_point_count_snow_on': load_point_count(sfm_snow_on).ravel(),
        'point_spread_snow_on': elevation_spread(sfm_snow_on).ravel(),
        'sfm_point_count_snow_free': load_point_count(sfm_snow_free).ravel(),
        'point_spread_snow_free': elevation_spread(sfm_snow_free).ravel(),
        'casi_class': casi_classification.ravel(),
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

# Index expermiment
# cursor = DB_CONNECTION.cursor()
# cursor.execute('CREATE INDEX sfm_depth_index ON ERW_analysis (sfm_snow_depth)')
# cursor.execute('CREATE INDEX casi_class_index ON ERW_analysis (casi_class)')
# DB_CONNECTION.commit()
