from pathlib import PurePath

import pytest


@pytest.fixture(scope='session')
def fixture_path():
    return PurePath(__file__).with_name('fixtures')


@pytest.fixture(scope='module')
def tmp_input_path(tmpdir_factory):
    return tmpdir_factory.mktemp('test_input_path')
