import pkg_resources
import pyogrio
from pyogrio import read_dataframe

pyogrio.core._register_drivers()

def load_shapefile():
    """Return a geodataframe with the polygon from a shapefile.
    """
    stream = pkg_resources.resource_stream(__name__, 'data/polygon.shp')
    return read_dataframe(stream)