from setuptools import setup

setup(
    name='raster-compare',
    version='0.1',
    packages=[
        'raster_compare.base',
        'raster_compare.plots',
    ],
    url='https://github.com/jomey/raster_compare',
    author='Joachim Meyer',
    author_email='j.meyer@utah.edu',
    description='Raster comparison tools',
    install_requires=[
        'gdal',
        'matplotlib',
        'numba',
        'numpy',
        'opencv-python',
        'palettable',
        'pandas',
        'pillow',
        'scipy',
        'statsmodels'
    ],
    extras_require={
        'dev': [
            'flake8',
            'pytest',
        ]
    }
)
