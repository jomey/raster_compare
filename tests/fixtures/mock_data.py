import numpy
from osgeo import gdal, gdalnumeric, osr

FILE_NAME = 'test_raster.tif'
GEO_TRANSFORM = (100., 1., 0., 100., 0., -1.)
NO_DATA_VALUE = 255
BAND_VALUES = numpy.array([
    [2, 3, 1],
    [1, 2, NO_DATA_VALUE],
    [NO_DATA_VALUE, 1, 4]
], dtype=numpy.uint8)

GDAL_DRIVER = gdal.GetDriverByName('GTiff')
PROJECTION = osr.SpatialReference()
PROJECTION.ImportFromEPSG(4326)


def raster_file(tmp_input_path):
    file_name = str(tmp_input_path / FILE_NAME)
    output_file = GDAL_DRIVER.Create(
        file_name,
        BAND_VALUES.shape[1],
        BAND_VALUES.shape[0],
        gdal.GDT_Byte
    )

    output_file.SetGeoTransform(GEO_TRANSFORM)
    output_file.SetProjection(PROJECTION.ExportToWkt())

    target_band = output_file.GetRasterBand(1)
    target_band.SetNoDataValue(NO_DATA_VALUE)
    gdalnumeric.BandWriteArray(target_band, BAND_VALUES)

    del target_band
    del output_file

    return file_name
