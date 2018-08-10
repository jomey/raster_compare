import pdal

from matplotlib import pyplot

NUM_BINS = 50
ROOT_PATH = '/Volumes/warehouse/projects/UofU/ASO/SB_20170221/'


def read_laz():
    json = """
    {
       "pipeline":[
            {
              "type":"readers.las",
              "filename":"/Volumes/warehouse/projects/UofU/ASO/SB_20170221/lidar/CO_merge_5m_sample.laz"
            }
      ]
    }"""

    pipeline = pdal.Pipeline(json)
    pipeline.validate()
    pipeline.execute()
    arrays = pipeline.arrays

    return arrays


def make_plot():
    lidar = read_laz()[0]
    pyplot.hist(lidar['Z'], bins=NUM_BINS, alpha=0.5, label='lidar', color='g')
    pyplot.xlim(lidar['Z'].min(), lidar['Z'].max())
    pyplot.xlim(lidar['Z'].min(), lidar['Z'].max())
    pyplot.ylabel('Count')
    pyplot.xlabel('Elevation')
    pyplot.title('Point cloud elevations')

    pyplot.savefig(ROOT_PATH + '/histogram.png')


if __name__ == '__main__':
    make_plot()
