import pytest

import numpy
from raster_compare.base import RasterFile, MedianAbsoluteDeviation
from tests.fixtures import mock_data


@pytest.fixture(scope='module')
def raster_file_name(tmp_input_path):
    return mock_data.raster_file(tmp_input_path)


@pytest.fixture(scope='module')
def subject(raster_file_name):
    return RasterFile(raster_file_name, TestRasterFile.BAND_NUMBER)


class TestRasterFile(object):
    BAND_NUMBER = 1

    def test_file_name(self, subject, raster_file_name):
        assert subject.file.GetDescription() == raster_file_name

    def test_checks_file_exists(self, subject):
        with pytest.raises(FileNotFoundError):
            subject.file = '/tmp/does_not_extist.tif'

    def test_band_number(self, subject):
        assert subject.band_number == self.BAND_NUMBER

    def test_set_band_number(self, subject):
        new_band = 2
        subject.band_number = new_band
        assert subject.band_number == new_band
        subject.band_number = self.BAND_NUMBER

    def test_mad(self, subject):
        assert isinstance(subject.mad, MedianAbsoluteDeviation)

    def test_geo_transform(self, subject):
        assert subject.geo_transform() == mock_data.GEO_TRANSFORM

    def test_extent(self, subject):
        assert subject.extent == (100.0, 103.0, 97.0, 100.0)

    def test_band_values(self, subject):
        numpy.testing.assert_equal(
            subject.band_values(),
            mock_data.BAND_VALUES
        )

    def test_band_values_masked(self, subject):
        assert subject.band_values().mask.any()
