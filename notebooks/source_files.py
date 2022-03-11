import pandas as pd
import sqlite3 as sql

from source_files_extended import *

ORTHO_IMAGE = HOME_DIR / 'Orthomosaic/ERW_20180524_Agisoft_rgb_5m_ortho.tif'

DB_CONNECTION = sql.connect(HOME_DIR / "erw_analysis.db")

HILLSHADE_SNOW_ON = dict(azimuth=101, altitude=47)
HILLSHADE_SNOW_FREE = dict(azimuth=247, altitude=32)


def db_query_to_df(query=None):
    if not query:
        query = 'Select * from ERW_analysis'
    df = pd.read_sql_query(query, DB_CONNECTION)

    if 'casi_class' in df:
        df['casi_class'] = pd.cut(
            df['casi_class'], CASI_MAPPING, labels=CASI_CLASSES
        )

    return df


def df_for_3m():
    aso_snow_depth_values = load_aso_depth()
    dem_file, elevation_data = load_reference_dem(aso_snow_depth_values.mask)

    df = pd.DataFrame(
        {
            'aso_snow_depth': aso_snow_depth_values.ravel(),
            'sfm_snow_depth': load_sfm_depth(aso_snow_depth_values.mask).ravel(),
            'elevation': elevation_data.ravel(),
            'slope': dem_file.slope.ravel(),
            'casi_class': load_classifier_data(aso_snow_depth_values.mask).ravel(),
        }
    )

    df.dropna(
        inplace=True,
        how='all',
        subset=['aso_snow_depth', 'sfm_snow_depth']
    )

    df['slope'] = df['slope'].fillna(-1).astype('int16')
    df['sd_difference'] = df.sfm_snow_depth - df.aso_snow_depth

    df['casi_class'] = pd.cut(
        df['casi_class'], CASI_MAPPING, labels=CASI_CLASSES
    )
    # Treat water and vegetation as one; water was misclassified
    df.loc[df['casi_class'] == 'Water', 'casi_class'] = 'Vegetation'

    return df

###
# CASI Classification
###

SNOW = 1.
VEGETATION = 2.
ROCK = 3.
WATER = 4.

CASI_MAPPING = [0., 1., 2., 3., np.inf]
CASI_CLASSES = ['Snow', 'Vegetation', 'Rock', 'Water']
CASI_COLORS = ['#4588b2', '#88a092', '#ffd8b1', '#88a092']
