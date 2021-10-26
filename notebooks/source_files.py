from pathlib import PurePath

import numpy as np
import os
import pandas as pd
import sqlite3 as sql

from raster_compare.base import RasterFile

HOME_DIR = PurePath(f"{os.environ['HOME']}/project-data/ERW-Paper")

SNOW_DEPTH_DIR = HOME_DIR / '1m'

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

